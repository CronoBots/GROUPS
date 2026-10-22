-- LES RÉPONSES DU CLIENT DU 23/10/2026 sur les heures supplémentaires et
-- les signatures (docs/questions-client.md) :
--
--  1. « Après le visa du responsable, la RH doit-elle confirmer ou
--     enregistrer la demande, comme pour les congés ? — Oui. » Les heures
--     supplémentaires suivent donc : demandeur → responsable d'équipe (le
--     contremaître de la pause ce jour-là, confirmé par le client) → RH,
--     qui enregistre (ou refuse, motif à l'appui). La RH ne confirme pas
--     avec le compte qui a visé comme responsable.
--     Sans toucher à la contrainte du statut (la changer demanderait de
--     la supprimer) : « approuvee » sans rh_le = chez la RH ; « approuvee »
--     avec rh_le = enregistrée ; un refus de la RH passe « refusee » avec
--     rh_motif.
--  2. « Sur une demande d'heures supplémentaires, il faut ajouter l'option
--     HS ou Flex time ; attention, le flex time c'est par heure, tandis
--     que les HS se prennent par 1/4 d'heure. » Colonne « type » (HS, FT)
--     et la durée en conséquence : HS par quart d'heure, FT par heure
--     entière. « En automatisant cela, cela permettra d'avoir toutes les
--     heures supplémentaires dont on n'avait pas de suivi avant » : la
--     liste porte le type et l'enregistrement, l'application en fait les
--     totaux.
--  3. « Pour les demandes de contremaître, les 2 contremaîtres impliqués
--     dans une demande de changement de pause ne peuvent pas signer leurs
--     feuilles » : celui qui figure comme remplaçant sur une demande ne
--     signe ni l'étape du contremaître ni celle de la RH ; le demandeur ne
--     signait déjà pas la sienne.
--  4. « Pour les heures supplémentaires de contremaître, le contremaître
--     ne peut pas non plus signer sa feuille » : c'était déjà la règle
--     (on ne vise pas sa propre demande) ; elle vaut aussi pour la RH.
--
-- Aucune suppression : les nouvelles fonctions (demander avec le type,
-- la liste élargie, enregistrer) s'ajoutent ; les anciennes restent.

alter table biowanze.heures_sup add column if not exists type text not null default 'HS';
alter table biowanze.heures_sup add column if not exists rh_par uuid;
alter table biowanze.heures_sup add column if not exists rh_le timestamptz;
alter table biowanze.heures_sup add column if not exists rh_motif text;
alter table biowanze.heures_sup add constraint heures_sup_type check (type in ('HS','FT'));
alter table biowanze.heures_sup add constraint heures_sup_pas check ((type = 'HS' and minutes % 15 = 0) or (type = 'FT' and minutes % 60 = 0));

-- la décision d'une demande de congé (base/23, une garde ajoutée)
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
    if jr.cellule is null or jr.cellule = '-' then continue; end if;
    if l ? 'pause' then
      cel := l->>'pause'; ann := jr.annotation;
      com := 'changement '||jr.cellule||' -> '||cel||' (demande n° '||d.id||')';
    else
      cel := jr.cellule; ann := l->>'code';
      com := 'Demande n° '||d.id
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

create or replace function public.biowanze_demander_hs(p_type text, p_jour date, p_horaire text, p_minutes int, p_justif text,
  p_justif_texte text, p_rappel_de text, p_responsable text, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare nid bigint;
begin
  if p_type not in ('HS','FT') then raise exception 'choisissez HS ou flex time'; end if;
  if p_type = 'HS' and p_minutes % 15 <> 0 then raise exception 'les HS se prennent par quart d''heure'; end if;
  if p_type = 'FT' and p_minutes % 60 <> 0 then raise exception 'le flex time se prend par heure entière'; end if;
  nid := public.biowanze_demander_hs(p_jour, p_horaire, p_minutes, p_justif, p_justif_texte, p_rappel_de, p_responsable, p_texte);
  update biowanze.heures_sup set type = p_type where id = nid;
  return nid;
end $$;

create or replace function public.biowanze_liste_hs2()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, type text, jour date, horaire text, minutes int,
               justif text, justif_texte text, rappel_de text, responsable text, texte text, statut text,
               visa_qui text, visa_le timestamptz, restriction text, motivation text, rappel_le date, motif_refus text,
               rh_qui text, rh_le timestamptz, rh_motif text,
               cree_le timestamptz, a_moi boolean, je_vise boolean, j_enregistre boolean)
language sql stable security definer set search_path = '' as $$
  select h.id, p.trigramme, p.nom, p.prenom, p.categorie, h.type, h.jour, h.horaire, h.minutes, h.justif, h.justif_texte, h.rappel_de,
         h.responsable, h.texte, h.statut, pv.trigramme, h.visa_le, h.restriction, h.motivation, h.rappel_le, h.motif_refus,
         pr.trigramme, h.rh_le, h.rh_motif, h.cree_le,
         h.personne_id = biowanze.ma_personne(),
         (h.statut = 'en_attente' and h.personne_id <> coalesce(biowanze.ma_personne(),'00000000-0000-0000-0000-000000000000'::uuid)
          and (h.responsable = biowanze.ma_trigramme() or (h.responsable is null and biowanze.role_courant() in ('rh','hierarchie')))),
         (h.statut = 'approuvee' and h.rh_le is null and biowanze.role_courant() = 'rh'
          and h.personne_id <> coalesce(biowanze.ma_personne(),'00000000-0000-0000-0000-000000000000'::uuid)
          and h.visa_par is distinct from auth.uid())
  from biowanze.heures_sup h
  join biowanze.personnes p on p.id = h.personne_id
  left join biowanze.comptes cv on cv.user_id = h.visa_par left join biowanze.personnes pv on pv.id = cv.personne_id
  left join biowanze.comptes cr on cr.user_id = h.rh_par left join biowanze.personnes pr on pr.id = cr.personne_id
  where biowanze.role_courant() is not null and h.statut <> 'annulee'
    and (biowanze.role_courant() in ('rh','hierarchie') or h.personne_id = biowanze.ma_personne() or h.responsable = biowanze.ma_trigramme())
  order by (h.statut = 'en_attente' or (h.statut = 'approuvee' and h.rh_le is null)) desc, h.jour desc, h.id desc
$$;

create or replace function public.biowanze_enregistrer_hs(p_id bigint, p_ok boolean, p_motif text)
returns text language plpgsql security definer set search_path = '' as $$
declare h record;
begin
  if coalesce(biowanze.role_courant() <> 'rh', true) then raise exception 'réservé au bureau RH'; end if;
  select * into h from biowanze.heures_sup where id = p_id for update;
  if not found or h.statut <> 'approuvee' or h.rh_le is not null then raise exception 'demande introuvable, pas encore visée par le responsable, ou déjà enregistrée'; end if;
  if h.personne_id = biowanze.ma_personne() then raise exception 'on n''enregistre pas sa propre demande'; end if;
  if h.visa_par = auth.uid() then raise exception 'la RH enregistre avec un autre compte que celui qui a visé comme responsable'; end if;
  if not p_ok and nullif(trim(coalesce(p_motif,'')),'') is null then raise exception 'un refus se motive'; end if;
  update biowanze.heures_sup set statut = case when p_ok then 'approuvee' else 'refusee' end,
         rh_par = auth.uid(), rh_le = now(), rh_motif = nullif(trim(coalesce(p_motif,'')),'') where id = p_id;
  return case when p_ok then 'enregistree' else 'refusee' end;
end $$;

create or replace function biowanze.hs_notifier()
returns trigger language plpgsql security definer set search_path = '' as $$
declare dem text; quoi text; n int := 0; u text := './?vue=heures';
begin
  select trigramme into dem from biowanze.personnes where id = new.personne_id;
  -- sans le type : à l'insertion, il n'est posé qu'après (biowanze_demander_hs à neuf arguments)
  quoi := (new.minutes / 60)||' h'||case when new.minutes % 60 > 0 then ' '||lpad((new.minutes % 60)::text,2,'0') else '' end
          ||' le '||to_char(new.jour,'DD/MM');
  if tg_op = 'INSERT' then
    if new.responsable is not null then
      insert into biowanze.notifs(tri, titre, texte, url) values (new.responsable, 'Heures supplémentaires à viser',
        coalesce(dem,'?')||' : '||quoi||'. Touchez pour viser.', u);
    else
      insert into biowanze.notifs(tri, titre, texte, url) select distinct p.trigramme, 'Heures supplémentaires à viser',
        coalesce(dem,'?')||' : '||quoi||'.', u
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id
       where c.role in ('rh','hierarchie') and c.valide and p.trigramme is not null and p.trigramme is distinct from dem;
    end if;
    n := 1;
  elsif new.rh_le is not null and old.rh_le is null and dem is not null then
    insert into biowanze.notifs(tri, titre, texte, url) values (dem,
      case new.statut when 'approuvee' then 'Heures supplémentaires enregistrées' else 'Heures supplémentaires refusées' end,
      'Votre demande ('||quoi||') est '||case new.statut when 'approuvee' then 'enregistrée par la RH' else 'refusée par la RH'||coalesce(' : '||new.rh_motif,'') end||'.', u);
    n := 1;
  elsif new.statut is distinct from old.statut and new.statut in ('approuvee','refusee') then
    if new.statut = 'approuvee' then
      insert into biowanze.notifs(tri, titre, texte, url) select distinct p.trigramme, 'Heures supplémentaires à enregistrer',
        coalesce(dem,'?')||' : '||quoi||', visées par le responsable.', u
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id
       where c.role = 'rh' and c.valide and p.trigramme is not null and p.trigramme is distinct from dem and c.user_id is distinct from new.visa_par;
    end if;
    if dem is not null then
      insert into biowanze.notifs(tri, titre, texte, url) values (dem,
        case new.statut when 'approuvee' then 'Heures supplémentaires visées' else 'Heures supplémentaires refusées' end,
        'Votre demande ('||quoi||') est '||case new.statut when 'approuvee' then 'visée par le responsable'||coalesce(', avec restriction : '||new.restriction,'')||' : elle part à la RH'
          else 'refusée'||coalesce(' : '||new.motif_refus,'') end||'.', u);
    end if;
    n := 1;
  end if;
  if n > 0 then perform biowanze.lancer_notifs(); end if;
  return new;
end $$;
create or replace trigger hs_notifier after insert or update of statut, rh_le on biowanze.heures_sup
  for each row execute function biowanze.hs_notifier();

revoke all on function public.biowanze_demander_hs(text,date,text,int,text,text,text,text,text) from public, anon;
revoke all on function public.biowanze_liste_hs2() from public, anon;
revoke all on function public.biowanze_enregistrer_hs(bigint,boolean,text) from public, anon;
grant execute on function public.biowanze_demander_hs(text,date,text,int,text,text,text,text,text) to authenticated;
grant execute on function public.biowanze_liste_hs2() to authenticated;
grant execute on function public.biowanze_enregistrer_hs(bigint,boolean,text) to authenticated;
