-- REVUE DE SÉCURITÉ DU 28/10/2026 (le client : « go complet », les skills
-- en renfort). Lue sur l'état RÉEL de la base (pg_get_functiondef), chaque
-- constat revérifié avant correction. Quatre trous, quatre corrections.
-- APPLIQUÉE le 28/10/2026 au soir par le client, dans l'éditeur SQL de
-- Supabase (le connecteur échouait : voir docs/journal/02-mises-a-jour.md).

-- 1. LES NOTIFICATIONS D'UN AUTRE. biowanze_abonner, ouverte à anon, prenait
--    le trigramme que le client lui donnait : n'importe qui, sans compte,
--    pouvait s'abonner sous le trigramme d'un contremaître ou de la RH et
--    recevoir ses notifications de demandes (« Demande de congé à viser »,
--    « Recyclage refusé : <motif> »). Le trigramme reste noté (le message
--    du classeur, déjà public dans data/, en dépend) mais il n'est SÛR que
--    si la session le confirme (tri_sur) ; le robot n'envoie les messages
--    des demandes qu'aux abonnements sûrs (tools/envoyer-push.js).
alter table biowanze.abonnements_push add column if not exists tri_sur boolean not null default false;

create or replace function public.biowanze_abonner(p_endpoint text, p_p256dh text, p_auth text, p_tri text)
returns void language plpgsql security definer set search_path = '' as $$
declare t text := biowanze.ma_trigramme();   -- null sans session validée
begin
  if p_endpoint !~ '^https://' or length(p_endpoint) > 1000
     or length(coalesce(p_p256dh,'')) not between 20 and 200
     or length(coalesce(p_auth,'')) not between 8 and 100
     or length(coalesce(p_tri,'')) > 10 then
    raise exception 'abonnement refusé';
  end if;
  insert into biowanze.abonnements_push(endpoint,p256dh,auth,tri,tri_sur,maj)
  values (p_endpoint,p_p256dh,p_auth,nullif(p_tri,''),coalesce(t = nullif(p_tri,''),false),now())
  on conflict (endpoint) do update set p256dh=excluded.p256dh, auth=excluded.auth, tri=excluded.tri,
    tri_sur=excluded.tri_sur, maj=now();
end $$;

drop function if exists public.biowanze_abonnes(text);
create function public.biowanze_abonnes(p_cle text)
returns table(endpoint text, p256dh text, auth text, tri text, tri_sur boolean)
language plpgsql security definer set search_path = '' as $$
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  return query select b.endpoint, b.p256dh, b.auth, b.tri, b.tri_sur from biowanze.abonnements_push b;
end $$;
revoke all on function public.biowanze_abonnes(text) from public;
grant execute on function public.biowanze_abonnes(text) to anon, authenticated;

-- 2. LE VISA DES HEURES SUP SANS CONTREMAÎTRE. L'ancienne version à huit
--    arguments de biowanze_demander_hs restait appelable et ne vérifiait
--    pas que le responsable est un contremaître : un opérateur en nommait
--    un autre, qui visait. La version à neuf arguments l'appelle en
--    SECURITY DEFINER : retirer le droit ne la casse pas. Et le visa exige,
--    hors RH et hiérarchie, que le responsable soit bien un contremaître.
revoke execute on function public.biowanze_demander_hs(date,text,integer,text,text,text,text,text) from public, anon, authenticated;

create or replace function public.biowanze_viser_hs(p_id bigint, p_ok boolean, p_restriction text, p_motivation text, p_rappel_le date)
returns text language plpgsql security definer set search_path = '' as $$
declare h record; moi text := biowanze.ma_trigramme(); r biowanze.role := biowanze.role_courant();
  cadre boolean := exists (select 1 from biowanze.personnes where trigramme = biowanze.ma_trigramme() and categorie ilike 'contrema%');
begin
  select * into h from biowanze.heures_sup where id = p_id for update;
  if not found or h.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if h.personne_id = biowanze.ma_personne() then raise exception 'on ne vise pas sa propre demande'; end if;
  if r is null or not ((coalesce(h.responsable = moi, false) and cadre) or r in ('rh','hierarchie')) then raise exception 'réservé au responsable hiérarchique'; end if;
  if not p_ok and nullif(trim(coalesce(p_motivation,'')),'') is null then raise exception 'un refus se motive'; end if;
  if p_ok and nullif(trim(coalesce(p_restriction,'')),'') is not null and nullif(trim(coalesce(p_motivation,'')),'') is null then
    raise exception 'une restriction se motive';
  end if;
  if p_ok and h.justif = 'rappel' and p_rappel_le is null then raise exception 'en cas de rappel, la date du rappel est à donner'; end if;
  update biowanze.heures_sup set statut = case when p_ok then 'approuvee' else 'refusee' end,
         visa_par = auth.uid(), visa_le = now(),
         restriction = case when p_ok then nullif(trim(coalesce(p_restriction,'')),'') end,
         motivation = case when p_ok then nullif(trim(coalesce(p_motivation,'')),'') end,
         motif_refus = case when not p_ok then nullif(trim(coalesce(p_motivation,'')),'') end,
         rappel_le = case when p_ok then p_rappel_le end
   where id = p_id;
  return case when p_ok then 'approuvee' else 'refusee' end;
end $$;

-- 3. LA FICHE DE RECYCLAGE CONFIRMÉE PAR UN FAUX CONTREMAÎTRE. Le
--    demandeur choisit le contremaître de la fiche (tout trigramme
--    existant) : un opérateur en désignait un autre, qui confirmait. Même
--    garde que pour les heures sup.
create or replace function public.biowanze_confirmer_recyclage(p_id bigint, p_ok boolean, p_motif text)
returns text language plpgsql security definer set search_path = '' as $$
declare f record; moi text := biowanze.ma_trigramme(); r biowanze.role := biowanze.role_courant();
  cadre boolean := exists (select 1 from biowanze.personnes where trigramme = biowanze.ma_trigramme() and categorie ilike 'contrema%');
begin
  select * into f from biowanze.recyclages_fiches where id = p_id for update;
  if not found or f.statut <> 'en_attente' then raise exception 'fiche introuvable ou déjà traitée'; end if;
  if f.personne_id = biowanze.ma_personne() then raise exception 'on ne confirme pas sa propre fiche'; end if;
  if r is null or not ((coalesce(f.cm = moi, false) and cadre) or r in ('rh','hierarchie')) then raise exception 'réservé au contremaître de la pause'; end if;
  if not p_ok and nullif(trim(coalesce(p_motif,'')),'') is null then raise exception 'un refus se motive'; end if;
  update biowanze.recyclages_fiches set statut = case when p_ok then 'confirmee' else 'refusee' end,
         cm_par = auth.uid(), cm_le = now(), cm_motif = nullif(trim(coalesce(p_motif,'')),'') where id = p_id;
  return case when p_ok then 'confirmee' else 'refusee' end;
end $$;

-- 4. LE TRIGRAMME CHANGÉ PENDANT QUE LA RH VALIDE. Tant que son compte
--    attend, l'utilisateur peut se rattacher à un autre trigramme ; la RH
--    validait par user_id ce qu'elle avait vu à l'écran un instant plus
--    tôt. Le client envoie désormais le trigramme affiché (p_trigramme) :
--    s'il a changé entre-temps, rien n'est validé.
drop function if exists public.biowanze_valider_compte(uuid,text,boolean);
create function public.biowanze_valider_compte(p_user uuid, p_role text default 'operateur', p_valide boolean default true, p_trigramme text default null)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if biowanze.role_courant() is distinct from 'rh' then raise exception 'réservé à la RH'; end if;
  if p_role not in ('operateur','hierarchie','rh') then raise exception 'rôle inconnu'; end if;
  if p_user = auth.uid() then raise exception 'on ne se valide pas soi-même'; end if;
  update biowanze.comptes c
     set role = p_role::biowanze.role, valide = p_valide,
         valide_par = auth.uid(), valide_le = now()
   where c.user_id = p_user
     and (p_trigramme is null
          or c.personne_id is not distinct from (select p.id from biowanze.personnes p where p.trigramme = p_trigramme));
  if not found then raise exception 'compte inconnu, ou son trigramme a changé : rechargez la liste'; end if;
end $$;
revoke all on function public.biowanze_valider_compte(uuid,text,boolean,text) from public, anon;
grant execute on function public.biowanze_valider_compte(uuid,text,boolean,text) to authenticated;
