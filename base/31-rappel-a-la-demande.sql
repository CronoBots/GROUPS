-- VENIR TRAVAILLER UN REPOS : UN RAPPEL SEULEMENT À LA DEMANDE DE LA
-- HIÉRARCHIE (le client, le 24/10/2026 : « Pas de rappel si non demandé par
-- la hiérarchie »).
--
-- Une modification de pause posée sur un repos s'inscrit comme la pause
-- choisie, sans prime. Si le visa coche « À la demande de la ligne
-- hiérarchique » (a_la_demande), le commentaire ajoute « Rappel le JJ/MM »
-- (la date de la demande), que l'application lit comme le classeur : un
-- rappel, avec sa prime.
--
-- Repris de 30-annuler-ou-changer-un-conge.sql ; seule la ligne marquée
-- change.

create or replace function public.biowanze_decider_demande(p_id bigint, p_accepte boolean, p_motif text default null)
returns text language plpgsql security definer set search_path = '' as $$
declare moi biowanze.role := biowanze.role_courant(); d record; cm_requis boolean; j date; jr record; nb int := 0;
        l jsonb; cel text; ann text; com text;
begin
  if moi is null or moi not in ('rh','hierarchie') then raise exception 'réservé aux contremaîtres et à la RH'; end if;
  select * into d from biowanze.demandes where id = p_id for update;
  if not found or d.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.personne_id = biowanze.ma_personne() then raise exception 'on ne valide pas sa propre demande'; end if;
  -- les contremaîtres impliqués (le remplaçant d'un changement de pause)
  -- ne signent pas la feuille où ils figurent (le client, le 23/10/2026)
  if exists (select 1 from jsonb_array_elements(d.lignes) x where x->>'rp' = biowanze.ma_trigramme()) then
    raise exception 'vous figurez sur cette demande (remplaçant) : un autre contremaître ou la RH la signe';
  end if;
  cm_requis := biowanze.demande_cm_requis(d.cree_par);
  if moi = 'hierarchie' and d.valide_cm is not null then
    raise exception 'déjà validée par un contremaître : la RH décide ensuite';
  end if;
  if not p_accepte then
    update biowanze.demandes set statut = 'refusee', motif_refus = nullif(trim(p_motif),''),
      -- le refus se porte à l'étape où il est donné
      valide_cm = case when d.valide_cm is null then auth.uid() else valide_cm end,
      valide_cm_le = case when d.valide_cm is null then now() else valide_cm_le end,
      valide_rh = case when d.valide_cm is not null then auth.uid() else valide_rh end,
      valide_rh_le = case when d.valide_cm is not null then now() else valide_rh_le end
     where id = p_id;
    return 'refusee';
  end if;
  -- d'abord l'étape du contremaître (hiérarchie, ou un compte RH), puis la RH
  if cm_requis and d.valide_cm is null then
    update biowanze.demandes set valide_cm = auth.uid(), valide_cm_le = now() where id = p_id;
  elsif moi = 'hierarchie' then
    raise exception 'déjà validée par un contremaître : la RH confirme ensuite';
  else
    if d.valide_cm = auth.uid() then raise exception 'la RH confirme avec un autre compte que celui qui a validé comme contremaître'; end if;
    update biowanze.demandes set valide_rh = auth.uid(), valide_rh_le = now() where id = p_id;
  end if;
  select * into d from biowanze.demandes where id = p_id;
  if d.valide_rh is null or (cm_requis and d.valide_cm is null) then
    return 'validee_en_partie';
  end if;
  for l in select * from jsonb_array_elements(case when jsonb_array_length(d.lignes) > 0 then d.lignes
           else (select jsonb_agg(jsonb_build_object('j', g::date, 'code', d.code)) from generate_series(d.du, d.au, interval '1 day') g) end) loop
    j := (l->>'j')::date;
    select cellule, annotation, commentaire into jr from biowanze.journees where personne_id = d.personne_id and jour = j;
    -- un repos ne reçoit que la pause où l'on vient travailler ; un type
    -- de congé n'y retire rien (le client, le 24/10/2026)
    if (jr.cellule is null or jr.cellule = '-') and not (l ? 'pause') and not (l ? 'annule') then continue; end if;
    if jr.cellule is null and l ? 'annule' then continue; end if;
    if l ? 'annule' then
      -- le congé annulé : la journée retrouve sa pause (le client, le 24/10/2026)
      cel := jr.cellule; ann := null;
      com := 'congé '||coalesce(jr.annotation, l->>'avant', '')||' annulé (demande n° '||d.id||')';
    elsif l ? 'pause' then
      cel := l->>'pause'; ann := jr.annotation;
      com := 'changement '||coalesce(jr.cellule,'-')||' -> '||cel||' (demande n° '||d.id||')'
             -- venir travailler un repos : un rappel seulement si la ligne
             -- hiérarchique l'a demandé (le client, le 24/10/2026 : « Pas de
             -- rappel si non demandé par la hiérarchie ») ; écrit comme le
             -- classeur, « Rappel le JJ/MM », la date de la demande
             ||case when coalesce(jr.cellule,'-') = '-' and coalesce(d.a_la_demande,false)
                    then ' Rappel le '||to_char(d.cree_le at time zone 'Europe/Brussels','DD/MM') else '' end;
    else
      cel := jr.cellule; ann := l->>'code';
      com := 'Demande n° '||d.id
             ||coalesce(' · remplace '||(l->>'avant'),'')
             ||coalesce(' · + '||(l->>'code2'),'')
             ||case when l ? 'part' then ' · '||case when l->>'part' = 'quitte' then 'quitte à ' else 'arrive à ' end||(l->>'heure') else '' end
             ||coalesce(' : '||d.texte,'');
    end if;
    insert into biowanze.journees(personne_id, jour, cellule, annotation, commentaire, source, maj_par, maj_le)
      values (d.personne_id, j, cel, ann, com, 'saisie', auth.uid(), now())
    on conflict (personne_id, jour) do update set
      cl_cellule = case when biowanze.journees.source = 'classeur' then biowanze.journees.cellule else biowanze.journees.cl_cellule end,
      cl_annotation = case when biowanze.journees.source = 'classeur' then biowanze.journees.annotation else biowanze.journees.cl_annotation end,
      cl_commentaire = case when biowanze.journees.source = 'classeur' then biowanze.journees.commentaire else biowanze.journees.cl_commentaire end,
      cellule = excluded.cellule, annotation = excluded.annotation, commentaire = excluded.commentaire,
      source = 'saisie', maj_par = auth.uid(), maj_le = now();
    nb := nb + 1;
  end loop;
  update biowanze.demandes set statut = 'acceptee' where id = p_id;
  return 'acceptee:'||nb;
end $$;
