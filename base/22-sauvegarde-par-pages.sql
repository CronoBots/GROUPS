-- LA SAUVEGARDE PAR PAGES (22/10/2026). biowanze_sauvegarde lisait toute la
-- base en UNE requête ; depuis l'horaire 2027 (55 000 journées), elle passe
-- la limite de 3 s des appels publics (rôle anon) : « canceling statement
-- due to statement timeout », erreur 500 à chaque passage, et une relève
-- restée pendue 20 minutes le 22/10 au soir. Le robot lit désormais la liste
-- des tables, puis chaque table par pages de quelques milliers de lignes, et
-- reconstruit LE MÊME document qu'avant ({faite_le, version, <table>: […]}) :
-- la restauration ne change pas. Même clé du robot, mêmes droits.

create or replace function public.biowanze_sauvegarde_tables(p_cle text)
returns setof text language plpgsql security definer set search_path = '' as $$
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  return query select c.relname::text from pg_class c join pg_namespace n on n.oid = c.relnamespace
               where n.nspname = 'biowanze' and c.relkind = 'r' order by 1;
end $$;

create or replace function public.biowanze_sauvegarde_page(p_cle text, p_table text, p_depuis int, p_n int)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare v jsonb;
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  if not exists (select 1 from pg_class c join pg_namespace n on n.oid = c.relnamespace
                 where n.nspname = 'biowanze' and c.relkind = 'r' and c.relname = p_table) then
    raise exception 'table inconnue : %', p_table;
  end if;
  if p_depuis < 0 or p_n < 1 or p_n > 20000 then raise exception 'page invalide'; end if;
  execute format('select coalesce(jsonb_agg(to_jsonb(x)), ''[]''::jsonb) from (select * from biowanze.%I order by ctid offset %s limit %s) x',
                 p_table, p_depuis, p_n) into v;
  return v;
end $$;

grant execute on function public.biowanze_sauvegarde_tables(text) to anon, authenticated;
grant execute on function public.biowanze_sauvegarde_page(text,text,int,int) to anon, authenticated;
