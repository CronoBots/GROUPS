-- BIOWANZE, étape 2 : les comptes. Un collègue se connecte (code reçu par
-- e-mail), demande à être rattaché à son trigramme ; tant qu'un contremaître
-- ou la RH n'a pas validé, il ne lit rien. La RH donne les rôles ; la
-- hiérarchie valide les opérateurs (le client, le 20/10/2026 : « le RH et la
-- ligne hiérarchique » saisissent).
alter table biowanze.comptes add column if not exists valide boolean not null default false;
alter table biowanze.comptes add column if not exists email text;
alter table biowanze.comptes add column if not exists valide_par uuid references auth.users(id);
alter table biowanze.comptes add column if not exists valide_le timestamptz;

-- Le rôle ne compte que pour un compte VALIDÉ.
create or replace function biowanze.role_courant() returns biowanze.role
language sql stable security definer set search_path = '' as $$
  select role from biowanze.comptes where user_id = auth.uid() and valide
$$;

-- Qui suis-je, validé ou non (biowanze_moi, de 02-lecture.sql, ne disait pas
-- la validation).
create or replace function public.biowanze_mon_compte()
returns table (role text, valide boolean, trigramme text, nom text, prenom text, categorie text, statut text)
language sql stable security definer set search_path = '' as $$
  select c.role::text, c.valide, p.trigramme, p.nom, p.prenom, p.categorie, p.statut
  from biowanze.comptes c left join biowanze.personnes p on p.id = c.personne_id
  where c.user_id = auth.uid()
$$;

-- Demander le rattachement à un trigramme (une seule demande par compte ;
-- la refaire la remplace tant qu'elle n'est pas validée).
create or replace function public.biowanze_rattacher(p_trigramme text)
returns text language plpgsql security definer set search_path = '' as $$
declare pid uuid; deja boolean;
begin
  if auth.uid() is null then raise exception 'non connecté'; end if;
  select id into pid from biowanze.personnes where trigramme = upper(trim(p_trigramme)) and actif;
  if pid is null then raise exception 'trigramme inconnu'; end if;
  select valide into deja from biowanze.comptes where user_id = auth.uid();
  if deja then raise exception 'compte déjà validé'; end if;
  insert into biowanze.comptes(user_id, personne_id, role, email)
    values (auth.uid(), pid, 'operateur', auth.jwt()->>'email')
    on conflict (user_id) do update set personne_id = excluded.personne_id, email = excluded.email;
  return 'en_attente';
end $$;

-- Les comptes, pour la RH et la hiérarchie.
create or replace function public.biowanze_comptes()
returns table (user_id uuid, email text, trigramme text, role text, valide boolean, cree_le timestamptz)
language sql stable security definer set search_path = '' as $$
  select c.user_id, c.email, p.trigramme, c.role::text, c.valide, c.cree_le
  from biowanze.comptes c left join biowanze.personnes p on p.id = c.personne_id
  where biowanze.role_courant() in ('rh','hierarchie')
  order by c.valide, c.cree_le desc
$$;

-- Valider un compte (et en fixer le rôle). La hiérarchie valide des
-- opérateurs ; seule la RH donne « hiérarchie » ou « rh ».
create or replace function public.biowanze_valider_compte(p_user uuid, p_role text default 'operateur', p_valide boolean default true)
returns void language plpgsql security definer set search_path = '' as $$
declare moi biowanze.role := biowanze.role_courant();
begin
  if moi is null or moi = 'operateur' then raise exception 'réservé à la RH et à la hiérarchie'; end if;
  if p_role not in ('operateur','hierarchie','rh') then raise exception 'rôle inconnu'; end if;
  if moi = 'hierarchie' and p_role <> 'operateur' then raise exception 'seule la RH donne ce rôle'; end if;
  if p_user = auth.uid() then raise exception 'on ne se valide pas soi-même'; end if;
  if moi = 'hierarchie' and exists (select 1 from biowanze.comptes
       where user_id = p_user and valide and role <> 'operateur') then
    raise exception 'seule la RH modifie ce compte';
  end if;
  update biowanze.comptes
     set role = p_role::biowanze.role, valide = p_valide,
         valide_par = auth.uid(), valide_le = now()
   where user_id = p_user;
  if not found then raise exception 'compte inconnu'; end if;
end $$;

revoke all on function public.biowanze_mon_compte() from public, anon;
revoke all on function public.biowanze_rattacher(text) from public, anon;
revoke all on function public.biowanze_comptes() from public, anon;
revoke all on function public.biowanze_valider_compte(uuid,text,boolean) from public, anon;
grant execute on function public.biowanze_mon_compte() to authenticated;
grant execute on function public.biowanze_rattacher(text) to authenticated;
grant execute on function public.biowanze_comptes() to authenticated;
grant execute on function public.biowanze_valider_compte(uuid,text,boolean) to authenticated;
