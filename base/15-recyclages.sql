-- LES FICHES DE RECYCLAGE « POLYVALENCE » (le client, le 22/10/2026 : « il
-- faut aussi ajouter, comme pour les demandes de congé, les demandes de
-- polyvalence ; c'est la personne qui fait office de contremaître lors de
-- la pause de la demande qui doit valider si la polyvalence — le recyclage
-- à un autre poste — a été faite complètement et confirmer », avec la
-- « Fiche de suivi des recyclages polyvalence » du dossier RH, juin 2021).
--
-- Une table À PART de biowanze.demandes : biowanze_decider_demande y lirait
-- la pause d'une fiche comme une « modification de pause » et réécrirait
-- l'horaire. Le circuit de la fiche papier :
--   1. le membre du personnel remplit et signe : fonction, date, pause,
--      doublure (et titulaire du poste) ;
--   2. le contremaître DE CETTE PAUSE confirme « avoir été averti au plus
--      tard en début de pause » et « que le travailleur a effectué un
--      recyclage sur le poste » — ou refuse, motif à l'appui ;
--   3. EN DOUBLURE seulement, le responsable de zone contresigne
--      (« obligatoire si recyclage en doublure », dit la fiche) ;
--   4. le bureau RH valide et enregistre.
-- Qui est « responsable de zone » : question ouverte au client
-- (docs/questions-client.md). En attendant, un compte hiérarchie ou RH
-- contresigne ; la base n'a aujourd'hui que des comptes RH.
-- Le contremaître attendu est lu par l'application dans l'horaire (la
-- ligne « Contremaître » de la pause, comme au Planning) et gardé dans la
-- fiche ; peuvent confirmer : lui, ou à défaut la hiérarchie et la RH.
-- Les compteurs de recyclage restent ceux du classeur RH : une fiche
-- validée ne les change pas (le classeur est la seule source).

create table if not exists biowanze.recyclages_fiches (
  id bigserial primary key,
  personne_id uuid not null references biowanze.personnes(id),
  fonction text not null check (fonction in ('Meunerie','Gluten','Fermentation','Distillation','Chaudières','Contremaître')),
  jour date not null,
  pause text not null check (pause in ('AM','PM','N','D')),
  doublure boolean not null default false,
  titulaire text,
  cm text,
  texte text,
  statut text not null default 'en_attente' check (statut in ('en_attente','confirmee','validee','refusee','annulee')),
  cm_par uuid, cm_le timestamptz, cm_motif text,
  zone_par uuid, zone_le timestamptz,
  rh_par uuid, rh_le timestamptz, rh_motif text,
  cree_par uuid, cree_le timestamptz not null default now()
);
alter table biowanze.recyclages_fiches enable row level security;
revoke all on biowanze.recyclages_fiches from public, anon, authenticated;
create unique index if not exists recyclages_fiches_une_par_pause on biowanze.recyclages_fiches (personne_id, jour, pause)
  where statut <> 'annulee' and statut <> 'refusee';

create or replace function public.biowanze_demander_recyclage(p_fonction text, p_jour date, p_pause text,
  p_doublure boolean, p_titulaire text, p_cm text, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); moi text := biowanze.ma_trigramme(); nid bigint; tit text; cm text;
begin
  if pid is null then raise exception 'compte non validé'; end if;
  if p_jour is null or p_jour > current_date + 60 or p_jour < current_date - 366 then raise exception 'date du recyclage invalide'; end if;
  tit := upper(nullif(trim(coalesce(p_titulaire,'')),''));
  if coalesce(p_doublure,false) and tit is null then raise exception 'en doublure, le titulaire du poste est à nommer'; end if;
  if tit is not null and not exists (select 1 from biowanze.personnes where trigramme = tit) then raise exception 'titulaire inconnu : %', tit; end if;
  if tit = moi then raise exception 'on ne se double pas soi-même'; end if;
  cm := upper(nullif(trim(coalesce(p_cm,'')),''));
  if cm is not null and not exists (select 1 from biowanze.personnes where trigramme = cm) then cm := null; end if;
  if exists (select 1 from biowanze.recyclages_fiches f where f.personne_id = pid and f.jour = p_jour and f.pause = p_pause and f.statut not in ('annulee','refusee')) then
    raise exception 'une fiche existe déjà pour cette pause (1 recyclage par pause prestée)';
  end if;
  insert into biowanze.recyclages_fiches(personne_id, fonction, jour, pause, doublure, titulaire, cm, texte, cree_par)
    values (pid, p_fonction, p_jour, p_pause, coalesce(p_doublure,false), tit, cm, nullif(trim(coalesce(p_texte,'')),''), auth.uid())
    returning id into nid;
  return nid;
end $$;

create or replace function public.biowanze_liste_recyclages()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, fonction text, jour date, pause text,
               doublure boolean, titulaire text, cm text, texte text, statut text,
               cm_qui text, cm_le timestamptz, cm_motif text, zone_qui text, zone_le timestamptz, rh_qui text, rh_le timestamptz, rh_motif text, cree_le timestamptz,
               a_moi boolean, je_confirme boolean, je_contresigne boolean, je_valide boolean)
language sql stable security definer set search_path = '' as $$
  select f.id, p.trigramme, p.nom, p.prenom, p.categorie, f.fonction, f.jour, f.pause, f.doublure, f.titulaire, f.cm, f.texte, f.statut,
         pc.trigramme, f.cm_le, f.cm_motif, pz.trigramme, f.zone_le, pr.trigramme, f.rh_le, f.rh_motif, f.cree_le,
         f.personne_id = biowanze.ma_personne(),
         (f.statut = 'en_attente' and f.personne_id <> coalesce(biowanze.ma_personne(),'00000000-0000-0000-0000-000000000000'::uuid)
          and (f.cm = biowanze.ma_trigramme() or (f.cm is null and biowanze.role_courant() in ('rh','hierarchie')))),
         (f.statut = 'confirmee' and f.doublure and f.zone_le is null and biowanze.role_courant() in ('rh','hierarchie')
          and f.personne_id <> coalesce(biowanze.ma_personne(),'00000000-0000-0000-0000-000000000000'::uuid)),
         (f.statut = 'confirmee' and (not f.doublure or f.zone_le is not null) and biowanze.role_courant() = 'rh')
  from biowanze.recyclages_fiches f
  join biowanze.personnes p on p.id = f.personne_id
  left join biowanze.comptes ccm on ccm.user_id = f.cm_par left join biowanze.personnes pc on pc.id = ccm.personne_id
  left join biowanze.comptes cz on cz.user_id = f.zone_par left join biowanze.personnes pz on pz.id = cz.personne_id
  left join biowanze.comptes crh on crh.user_id = f.rh_par left join biowanze.personnes pr on pr.id = crh.personne_id
  where biowanze.role_courant() is not null
    and (biowanze.role_courant() in ('rh','hierarchie') or f.personne_id = biowanze.ma_personne() or f.cm = biowanze.ma_trigramme())
  order by (f.statut in ('en_attente','confirmee')) desc, f.jour desc, f.id desc
$$;

create or replace function public.biowanze_confirmer_recyclage(p_id bigint, p_ok boolean, p_motif text)
returns text language plpgsql security definer set search_path = '' as $$
declare f record; moi text := biowanze.ma_trigramme(); r biowanze.role := biowanze.role_courant();
begin
  select * into f from biowanze.recyclages_fiches where id = p_id for update;
  if not found or f.statut <> 'en_attente' then raise exception 'fiche introuvable ou déjà traitée'; end if;
  if f.personne_id = biowanze.ma_personne() then raise exception 'on ne confirme pas sa propre fiche'; end if;
  if r is null or not (coalesce(f.cm = moi, false) or r in ('rh','hierarchie')) then raise exception 'réservé au contremaître de la pause'; end if;
  if not p_ok and nullif(trim(coalesce(p_motif,'')),'') is null then raise exception 'un refus se motive'; end if;
  update biowanze.recyclages_fiches set statut = case when p_ok then 'confirmee' else 'refusee' end,
         cm_par = auth.uid(), cm_le = now(), cm_motif = nullif(trim(coalesce(p_motif,'')),'') where id = p_id;
  return case when p_ok then 'confirmee' else 'refusee' end;
end $$;

create or replace function public.biowanze_contresigner_recyclage(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
declare f record;
begin
  if coalesce(biowanze.role_courant() not in ('rh','hierarchie'), true) then raise exception 'réservé au responsable de zone'; end if;
  select * into f from biowanze.recyclages_fiches where id = p_id for update;
  if not found or f.statut <> 'confirmee' or not f.doublure or f.zone_le is not null then
    raise exception 'fiche introuvable, sans doublure, non confirmée ou déjà contresignée';
  end if;
  if f.personne_id = biowanze.ma_personne() then raise exception 'on ne contresigne pas sa propre fiche'; end if;
  update biowanze.recyclages_fiches set zone_par = auth.uid(), zone_le = now() where id = p_id;
  return 'contresignee';
end $$;

create or replace function public.biowanze_valider_recyclage(p_id bigint, p_ok boolean, p_motif text)
returns text language plpgsql security definer set search_path = '' as $$
declare f record;
begin
  if coalesce(biowanze.role_courant() <> 'rh', true) then raise exception 'réservé au bureau RH'; end if;
  select * into f from biowanze.recyclages_fiches where id = p_id for update;
  if not found or f.statut <> 'confirmee' then raise exception 'fiche introuvable, non confirmée par le contremaître, ou déjà traitée'; end if;
  if f.personne_id = biowanze.ma_personne() then raise exception 'on ne valide pas sa propre fiche'; end if;
  if p_ok and f.doublure and f.zone_le is null then raise exception 'en doublure, le responsable de zone contresigne d''abord'; end if;
  if not p_ok and nullif(trim(coalesce(p_motif,'')),'') is null then raise exception 'un refus se motive'; end if;
  update biowanze.recyclages_fiches set statut = case when p_ok then 'validee' else 'refusee' end,
         rh_par = auth.uid(), rh_le = now(), rh_motif = nullif(trim(coalesce(p_motif,'')),'') where id = p_id;
  return case when p_ok then 'validee' else 'refusee' end;
end $$;

create or replace function public.biowanze_annuler_recyclage(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
begin
  update biowanze.recyclages_fiches set statut = 'annulee'
   where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente';
  if not found then raise exception 'fiche introuvable ou déjà traitée'; end if;
  return 'annulee';
end $$;

-- les notifications, par la file des demandes (14-remplacant-puis-rh.sql)
create or replace function biowanze.recyclages_notifier()
returns trigger language plpgsql security definer set search_path = '' as $$
declare dem text; quand text; n int := 0; u text := './?vue=recyclages';
begin
  select trigramme into dem from biowanze.personnes where id = new.personne_id;
  quand := to_char(new.jour,'DD/MM')||' ('||new.pause||')';
  if tg_op = 'INSERT' then
    if new.cm is not null then
      insert into biowanze.notifs(tri, titre, texte, url) values (new.cm, 'Recyclage à confirmer',
        coalesce(dem,'?')||' : recyclage '||new.fonction||' le '||quand||'. Touchez pour confirmer.', u);
    else
      insert into biowanze.notifs(tri, titre, texte, url) select distinct p.trigramme, 'Recyclage à confirmer',
        coalesce(dem,'?')||' : recyclage '||new.fonction||' le '||quand||' (contremaître de la pause non trouvé).', u
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id where c.role = 'rh' and c.valide and p.trigramme is not null and p.trigramme is distinct from dem;
    end if;
    n := 1;
  elsif new.zone_le is not null and old.zone_le is null then
    insert into biowanze.notifs(tri, titre, texte, url) select distinct p.trigramme, 'Recyclage à valider',
      coalesce(dem,'?')||' : recyclage en doublure '||new.fonction||' le '||quand||', contresigné par le responsable de zone.', u
      from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id where c.role = 'rh' and c.valide and p.trigramme is not null and p.trigramme is distinct from dem;
    n := 1;
  elsif new.statut is distinct from old.statut then
    if new.statut = 'confirmee' and new.doublure then
      insert into biowanze.notifs(tri, titre, texte, url) select distinct p.trigramme, 'Recyclage à contresigner',
        coalesce(dem,'?')||' : recyclage en doublure '||new.fonction||' le '||quand||', confirmé par le contremaître.', u
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id where c.role in ('rh','hierarchie') and c.valide and p.trigramme is not null and p.trigramme is distinct from dem;
      n := 1;
    elsif new.statut = 'confirmee' then
      insert into biowanze.notifs(tri, titre, texte, url) select distinct p.trigramme, 'Recyclage à valider',
        coalesce(dem,'?')||' : recyclage '||new.fonction||' le '||quand||', confirmé par le contremaître.', u
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id where c.role = 'rh' and c.valide and p.trigramme is not null and p.trigramme is distinct from dem;
      n := 1;
    end if;
    if new.statut in ('confirmee','validee','refusee') and dem is not null then
      insert into biowanze.notifs(tri, titre, texte, url) values (dem,
        case new.statut when 'confirmee' then 'Recyclage confirmé' when 'validee' then 'Recyclage enregistré' else 'Recyclage refusé' end,
        'Votre fiche '||new.fonction||' du '||quand||case new.statut when 'confirmee' then ' est confirmée par le contremaître : elle part chez la RH.'
          when 'validee' then ' est validée et enregistrée par la RH.' else ' est refusée'||coalesce(' : '||coalesce(new.rh_motif,new.cm_motif),'')||'.' end, u);
      n := 1;
    end if;
  end if;
  if n > 0 then perform biowanze.lancer_notifs(); end if;
  return new;
end $$;
revoke all on function biowanze.recyclages_notifier() from public, anon, authenticated;
create trigger recyclages_notifier after insert or update of statut, zone_le on biowanze.recyclages_fiches
  for each row execute function biowanze.recyclages_notifier();

revoke all on function public.biowanze_demander_recyclage(text,date,text,boolean,text,text,text) from public, anon;
revoke all on function public.biowanze_liste_recyclages() from public, anon;
revoke all on function public.biowanze_confirmer_recyclage(bigint,boolean,text) from public, anon;
revoke all on function public.biowanze_valider_recyclage(bigint,boolean,text) from public, anon;
revoke all on function public.biowanze_annuler_recyclage(bigint) from public, anon;
grant execute on function public.biowanze_demander_recyclage(text,date,text,boolean,text,text,text) to authenticated;
grant execute on function public.biowanze_liste_recyclages() to authenticated;
grant execute on function public.biowanze_confirmer_recyclage(bigint,boolean,text) to authenticated;
grant execute on function public.biowanze_valider_recyclage(bigint,boolean,text) to authenticated;
grant execute on function public.biowanze_annuler_recyclage(bigint) to authenticated;
revoke all on function public.biowanze_contresigner_recyclage(bigint) from public, anon;
grant execute on function public.biowanze_contresigner_recyclage(bigint) to authenticated;

-- (appliqué le 22/10/2026 avec execute_sql, en deux envois : la table et
-- les fonctions, puis le déclencheur ; aucune suppression.)
