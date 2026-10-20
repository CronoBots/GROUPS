-- BIOWANZE : les abonnements aux notifications rangés dans le schéma
-- `biowanze` (20/10/2026). La table vivait dans `public`, à côté des tables
-- de PINO ; elle passe dans le schéma à part, renommée, et les trois
-- fonctions de l'application et du robot la lisent là. La clé du robot est
-- vérifiée par biowanze.cle_robot (base/03-synchro.sql).
alter table public.biowanze_push set schema biowanze;
alter table biowanze.biowanze_push rename to abonnements_push;
create or replace function public.biowanze_abonner(p_endpoint text, p_p256dh text, p_auth text, p_tri text)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if p_endpoint !~ '^https://' or length(p_endpoint) > 1000
     or length(coalesce(p_p256dh,'')) not between 20 and 200
     or length(coalesce(p_auth,'')) not between 8 and 100
     or length(coalesce(p_tri,'')) > 10 then
    raise exception 'abonnement refusé';
  end if;
  insert into biowanze.abonnements_push(endpoint,p256dh,auth,tri,maj)
  values (p_endpoint,p_p256dh,p_auth,nullif(p_tri,''),now())
  on conflict (endpoint) do update set p256dh=excluded.p256dh, auth=excluded.auth, tri=excluded.tri, maj=now();
end $$;
create or replace function public.biowanze_abonnes(p_cle text)
returns table(endpoint text, p256dh text, auth text, tri text)
language plpgsql security definer set search_path = '' as $$
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  return query select b.endpoint, b.p256dh, b.auth, b.tri from biowanze.abonnements_push b;
end $$;
create or replace function public.biowanze_desabonner(p_endpoint text)
returns void language sql security definer set search_path = '' as $$
  delete from biowanze.abonnements_push where endpoint = p_endpoint;
$$;
