-- LE RESPONSABLE D'ÉQUIPE EST UN CONTREMAÎTRE OU UN ADJOINT (le client, le
-- 23/10/2026 : « les responsables d'équipe ne peuvent être que les
-- contremaîtres et/ou adjoints »). Ce sont les personnes de la catégorie
-- « Contremaîtres de production » du classeur (onze : six contremaîtres,
-- cinq adjoints). La feuille ne propose qu'eux ; la base refuse les autres.
create or replace function public.biowanze_demander_hs(p_type text, p_jour date, p_horaire text, p_minutes int, p_justif text,
  p_justif_texte text, p_rappel_de text, p_responsable text, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare nid bigint; resp text := upper(nullif(trim(coalesce(p_responsable,'')),''));
begin
  if p_type not in ('HS','FT') then raise exception 'choisissez HS ou flex time'; end if;
  if p_type = 'HS' and p_minutes % 15 <> 0 then raise exception 'les HS se prennent par quart d''heure'; end if;
  if p_type = 'FT' and p_minutes % 60 <> 0 then raise exception 'le flex time se prend par heure entière'; end if;
  if resp is not null and not exists (select 1 from biowanze.personnes where trigramme = resp and categorie ilike 'contrema%') then
    raise exception 'le responsable d''équipe est un contremaître ou un adjoint';
  end if;
  nid := public.biowanze_demander_hs(p_jour, p_horaire, p_minutes, p_justif, p_justif_texte, p_rappel_de, p_responsable, p_texte);
  update biowanze.heures_sup set type = p_type where id = nid;
  return nid;
end $$;
