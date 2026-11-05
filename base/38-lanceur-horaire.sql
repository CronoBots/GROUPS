-- LE LANCEUR DU ROBOT, VERSÉ AU DÉPÔT (check complet du 05/11/2026). Depuis
-- le 16/10/2026, ce n'est pas le planificateur de GitHub qui lance la mise à
-- jour automatique de l'horaire, mais la base (journal 02, « Le planificateur
-- de GitHub ne lançait rien ») : la tâche pg_cron « biowanze-horaire », toutes
-- les 15 minutes, appelle biowanze_lancer_horaire(), qui envoie un
-- workflow_dispatch à GitHub par pg_net. Ces deux pièces vivaient dans la base
-- seule : une base reconstruite depuis base/ les aurait perdues sans bruit.
--
-- Recopié tel quel de la base le 05/11/2026 (pg_get_functiondef, cron.job,
-- droits). AUCUN SECRET ICI : le jeton GitHub (accès au seul dépôt,
-- permission Actions en écriture) est dans le coffre de la base, secret
-- « biowanze_github », que le client dépose lui-même dans l'éditeur SQL. Sans
-- lui, la fonction ne fait rien. Elle n'est exécutable ni par anon ni par
-- authenticated.
--
-- Rejouer ce fichier ne change rien à une base qui l'a déjà : « create or
-- replace », et cron.schedule remplace une tâche du même nom.

create or replace function public.biowanze_lancer_horaire()
 returns bigint
 language plpgsql
 security definer
 set search_path to 'public', 'extensions', 'vault', 'net'
as $function$
declare
  jeton text;
begin
  select decrypted_secret into jeton from vault.decrypted_secrets where name = 'biowanze_github' limit 1;
  if jeton is null or jeton = '' then
    return null;
  end if;
  return net.http_post(
    url := 'https://api.github.com/repos/CronoBots/GROUPS/actions/workflows/horaire-auto.yml/dispatches',
    body := '{"ref":"main"}'::jsonb,
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || jeton,
      'Accept', 'application/vnd.github+json',
      'X-GitHub-Api-Version', '2022-11-28',
      'User-Agent', 'biowanze-horaire',
      'Content-Type', 'application/json')
  );
end;
$function$;

revoke all on function public.biowanze_lancer_horaire() from public, anon, authenticated;
grant execute on function public.biowanze_lancer_horaire() to service_role;

select cron.schedule('biowanze-horaire', '*/15 * * * *', 'select public.biowanze_lancer_horaire()');
