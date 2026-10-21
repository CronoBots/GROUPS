-- La sauvegarde de la base BIOWANZE. La formule gratuite de Supabase n'en
-- fait aucune ; avant que la RH saisisse dans l'application, il en faut une.
-- Le robot (tools/base-sauvegarde.py) l'appelle une fois par jour avec sa
-- clé, la compresse, la CHIFFRE avec cette même clé et l'envoie à sa propre
-- boîte Gmail — jamais au dépôt, qui est public. Tout le schéma biowanze,
-- table par table, et aussi les abonnements aux notifications.
create or replace function public.biowanze_sauvegarde(p_cle text)
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare r jsonb := jsonb_build_object('faite_le', now(), 'version', 1);
        t text; v jsonb;
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  for t in select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
           where n.nspname = 'biowanze' and c.relkind = 'r' order by 1 loop
    execute format('select coalesce(jsonb_agg(to_jsonb(x)), ''[]''::jsonb) from biowanze.%I x', t)
      into v;
    r := r || jsonb_build_object(t, v);
  end loop;
  return r;
end $$;
revoke all on function public.biowanze_sauvegarde(text) from public;
grant execute on function public.biowanze_sauvegarde(text) to anon;
