-- MODULE 3 DE LA PLATEFORME : les demandes de congé (le client, le
-- 21/10/2026 : « go pour le module Demandes »). Le circuit est celui du
-- 20/10 : « qui valide une demande d'un opérateur : les contremaîtres et
-- RH ». L'opérateur demande ; un contremaître (rôle hierarchie) ET la RH
-- valident, dans n'importe quel ordre ; un refus de l'un suffit. La
-- demande d'un cadre (hiérarchie, RH) n'attend que la RH. Nul ne valide
-- sa propre demande. Acceptée, elle POSE le code sur chaque jour de
-- travail de la période (le poste prévu reste, le repos est sauté), comme
-- une saisie : le classeur ne l'écrase plus.

-- les codes qu'on peut demander
create or replace function biowanze.code_demandable(p text)
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from biowanze.codes c where c.code = p and c.actif and c.famille in ('conge','recup'))
$$;
revoke all on function biowanze.code_demandable(text) from public, anon, authenticated;

create or replace function biowanze.ma_personne()
returns uuid language sql stable security definer set search_path = '' as $$
  select c.personne_id from biowanze.comptes c where c.user_id = auth.uid() and c.valide
$$;
revoke all on function biowanze.ma_personne() from public, anon, authenticated;

-- Demander.
create or replace function public.biowanze_demander(p_code text, p_du date, p_au date, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); nid bigint;
begin
  if pid is null then raise exception 'compte non validé'; end if;
  if not biowanze.code_demandable(p_code) then raise exception 'code non demandable : %', p_code; end if;
  if p_du is null or p_au is null or p_au < p_du then raise exception 'période invalide'; end if;
  if p_au - p_du > 62 then raise exception 'période trop longue (deux mois au plus)'; end if;
  if extract(year from p_du) <> extract(year from p_au) then raise exception 'une demande par année'; end if;
  if p_du < current_date - 31 then raise exception 'date trop ancienne'; end if;
  if exists (select 1 from biowanze.demandes d where d.personne_id = pid and d.statut = 'en_attente'
             and d.du <= p_au and d.au >= p_du) then
    raise exception 'une demande en attente couvre déjà ces jours';
  end if;
  insert into biowanze.demandes(personne_id, type, du, au, code, texte, cree_par)
    values (pid, 'conge', p_du, p_au, p_code, nullif(trim(p_texte),''), auth.uid())
    returning id into nid;
  return nid;
end $$;

-- Annuler sa demande, tant qu'elle attend.
create or replace function public.biowanze_annuler_demande(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
begin
  update biowanze.demandes set statut = 'annulee'
   where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente';
  if not found then raise exception 'demande introuvable ou déjà traitée'; end if;
  return 'annulee';
end $$;

-- Les demandes : les siennes pour chacun ; toutes pour la RH et la
-- hiérarchie. « attend_cm » / « attend_rh » disent ce qui manque.
create or replace function public.biowanze_demandes()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, code text, du date, au date, texte text,
               statut text, cm text, cm_le timestamptz, rh text, rh_le timestamptz, motif_refus text, cree_le timestamptz,
               attend_cm boolean, attend_rh boolean, a_moi boolean)
language sql stable security definer set search_path = '' as $$
  select d.id, p.trigramme, p.nom, p.prenom, p.categorie, d.code, d.du, d.au, d.texte, d.statut,
         pc.trigramme, d.valide_cm_le, pr.trigramme, d.valide_rh_le, d.motif_refus, d.cree_le,
         (d.statut = 'en_attente' and d.valide_cm is null and coalesce(cd.role,'operateur') = 'operateur'),
         (d.statut = 'en_attente' and d.valide_rh is null),
         d.personne_id = biowanze.ma_personne()
  from biowanze.demandes d
  join biowanze.personnes p on p.id = d.personne_id
  left join biowanze.comptes cd on cd.user_id = d.cree_par
  left join biowanze.comptes ccm on ccm.user_id = d.valide_cm left join biowanze.personnes pc on pc.id = ccm.personne_id
  left join biowanze.comptes crh on crh.user_id = d.valide_rh left join biowanze.personnes pr on pr.id = crh.personne_id
  where biowanze.role_courant() is not null
    and (biowanze.role_courant() in ('rh','hierarchie') or d.personne_id = biowanze.ma_personne())
  order by (d.statut = 'en_attente') desc, d.du, d.id
$$;

-- Décider : la hiérarchie au titre du contremaître, la RH au sien.
create or replace function public.biowanze_decider_demande(p_id bigint, p_accepte boolean, p_motif text default null)
returns text language plpgsql security definer set search_path = '' as $$
declare moi biowanze.role := biowanze.role_courant(); d record; role_dem biowanze.role; j date; jr record; nb int := 0;
begin
  if moi not in ('rh','hierarchie') then raise exception 'réservé aux contremaîtres et à la RH'; end if;
  select * into d from biowanze.demandes where id = p_id for update;
  if not found or d.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.personne_id = biowanze.ma_personne() then raise exception 'on ne valide pas sa propre demande'; end if;
  select coalesce(c.role,'operateur') into role_dem from biowanze.comptes c where c.user_id = d.cree_par;
  if not p_accepte then
    update biowanze.demandes set statut = 'refusee', motif_refus = nullif(trim(p_motif),''),
      valide_cm = case when moi = 'hierarchie' then auth.uid() else valide_cm end,
      valide_cm_le = case when moi = 'hierarchie' then now() else valide_cm_le end,
      valide_rh = case when moi = 'rh' then auth.uid() else valide_rh end,
      valide_rh_le = case when moi = 'rh' then now() else valide_rh_le end
     where id = p_id;
    return 'refusee';
  end if;
  if moi = 'hierarchie' then
    if coalesce(role_dem,'operateur') <> 'operateur' then raise exception 'la demande d''un cadre ne se valide que par la RH'; end if;
    update biowanze.demandes set valide_cm = auth.uid(), valide_cm_le = now() where id = p_id;
  else
    update biowanze.demandes set valide_rh = auth.uid(), valide_rh_le = now() where id = p_id;
  end if;
  select * into d from biowanze.demandes where id = p_id;
  if d.valide_rh is null or (coalesce(role_dem,'operateur') = 'operateur' and d.valide_cm is null) then
    return 'validee_en_partie';
  end if;
  -- acceptée : le code se pose sur chaque jour de travail de la période
  for j in select generate_series(d.du, d.au, interval '1 day')::date loop
    select cellule, annotation, commentaire, source, cl_cellule, cl_annotation, cl_commentaire into jr
      from biowanze.journees where personne_id = d.personne_id and jour = j;
    if jr.cellule is null or jr.cellule = '-' then continue; end if;
    insert into biowanze.journees(personne_id, jour, cellule, annotation, commentaire, source, maj_par, maj_le)
      values (d.personne_id, j, jr.cellule, d.code, 'Demande n° '||d.id||coalesce(' : '||d.texte,''), 'saisie', auth.uid(), now())
    on conflict (personne_id, jour) do update set
      cl_cellule = case when biowanze.journees.source = 'classeur' then biowanze.journees.cellule else biowanze.journees.cl_cellule end,
      cl_annotation = case when biowanze.journees.source = 'classeur' then biowanze.journees.annotation else biowanze.journees.cl_annotation end,
      cl_commentaire = case when biowanze.journees.source = 'classeur' then biowanze.journees.commentaire else biowanze.journees.cl_commentaire end,
      annotation = excluded.annotation, commentaire = excluded.commentaire,
      source = 'saisie', maj_par = auth.uid(), maj_le = now();
    nb := nb + 1;
  end loop;
  update biowanze.demandes set statut = 'acceptee' where id = p_id;
  return 'acceptee:'||nb;
end $$;

revoke all on function public.biowanze_demander(text,date,date,text) from public, anon;
revoke all on function public.biowanze_annuler_demande(bigint) from public, anon;
revoke all on function public.biowanze_demandes() from public, anon;
revoke all on function public.biowanze_decider_demande(bigint,boolean,text) from public, anon;
grant execute on function public.biowanze_demander(text,date,date,text) to authenticated;
grant execute on function public.biowanze_annuler_demande(bigint) to authenticated;
grant execute on function public.biowanze_demandes() to authenticated;
grant execute on function public.biowanze_decider_demande(bigint,boolean,text) to authenticated;
