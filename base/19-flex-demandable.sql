-- LE FLEX TIME SE DEMANDE AUSSI (le client, le 22/10/2026 : « il faut aussi
-- ajouter le FT au type de congé »). Une reprise de flex time (« 8h -FT »,
-- « 4h -FT »…, famille « flex ») se pose comme un congé : elle s'ajoute aux
-- codes demandables. Les « +FT » (heures prestées en plus) restent hors de
-- la liste : ce ne sont pas des absences.
create or replace function biowanze.code_demandable(p text)
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from biowanze.codes c where c.code = p and c.actif
                   and (c.famille in ('conge','recup') or (c.famille = 'flex' and c.code like '%-FT')))
$$;
revoke all on function biowanze.code_demandable(text) from public, anon, authenticated;
