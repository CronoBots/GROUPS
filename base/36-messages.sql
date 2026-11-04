-- LE FIL DE L'USINE (le client, le 04/11/2026 : « j'aimerais bien que tu
-- ajoutes un chat message pro comme cadre dans l'accueil », puis en QCM :
-- « usine seulement »). Un seul fil, commun à tous les comptes validés :
-- pas de messages privés, pas de fil par équipe.
--
-- Comme les annonces (base/35) : la table est fermée, on n'y accède que par
-- les fonctions ci-dessous, qui exigent un compte validé
-- (biowanze.role_courant) et signent chaque message du trigramme du compte
-- (biowanze.ma_trigramme). La sauvegarde quotidienne (base/22) reprend
-- d'office toute table du schéma.
--
-- Rien n'y est supprimé ni remplacé. Le serveur demande pourtant une
-- confirmation pour une table neuve (CLAUDE.md, « Une migration de la
-- base ») : ce fichier se colle dans l'éditeur SQL du projet.

create table if not exists biowanze.messages (
  id bigserial primary key,
  auteur text not null,                 -- le trigramme du compte qui écrit
  corps text not null check (length(btrim(corps)) between 1 and 1000),
  cree_le timestamptz not null default now(),
  efface_le timestamptz,                -- effacé : le texte disparaît, la trace reste
  efface_par text
);
create index if not exists messages_auteur_cree_le on biowanze.messages (auteur, cree_le desc);
alter table biowanze.messages enable row level security;
revoke all on biowanze.messages from public, anon, authenticated;
revoke all on sequence biowanze.messages_id_seq from public, anon, authenticated;

-- Lire : tout compte validé. Les 100 derniers, ou ceux qui suivent p_apres
-- (l'identifiant du dernier message déjà reçu), du plus ancien au plus récent.
-- Un message effacé revient sans son texte : le fil dit qu'il a été effacé.
create or replace function public.biowanze_messages(p_apres bigint default null)
returns table (id bigint, auteur text, corps text, cree_le timestamptz, efface boolean)
language plpgsql stable security definer set search_path = '' as $$
begin
  if biowanze.role_courant() is null then raise exception 'compte non validé'; end if;
  return query
    select m.id, m.auteur, case when m.efface_le is null then m.corps else '' end, m.cree_le, m.efface_le is not null
      from (select x.* from biowanze.messages x
             where p_apres is null or x.id > p_apres
             order by x.id desc limit 100) m
     order by m.id;
end $$;
revoke all on function public.biowanze_messages(bigint) from public, anon;
grant execute on function public.biowanze_messages(bigint) to authenticated;

-- Écrire : tout compte validé, sous son trigramme ; de 1 à 1 000 caractères ;
-- pas plus de dix messages par minute et par compte.
create or replace function public.biowanze_ecrire_message(p_corps text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare v_id bigint; c text := btrim(coalesce(p_corps,'')); t text;
begin
  if biowanze.role_courant() is null then raise exception 'compte non validé'; end if;
  t := biowanze.ma_trigramme();
  if t is null then raise exception 'compte sans trigramme'; end if;
  if length(c) not between 1 and 1000 then raise exception 'message de 1 à 1 000 caractères'; end if;
  if (select count(*) from biowanze.messages m
       where m.auteur = t and m.cree_le > now() - interval '1 minute') >= 10 then
    raise exception 'trop de messages en une minute, attendez un instant';
  end if;
  insert into biowanze.messages(auteur, corps) values (t, c) returning id into v_id;
  return v_id;
end $$;
revoke all on function public.biowanze_ecrire_message(text) from public, anon;
grant execute on function public.biowanze_ecrire_message(text) to authenticated;

-- Effacer : l'auteur, ou la RH (modération). Le texte disparaît du fil ;
-- l'heure, l'auteur et qui a effacé restent.
create or replace function public.biowanze_effacer_message(p_id bigint)
returns void language plpgsql security definer set search_path = '' as $$
declare t text := biowanze.ma_trigramme();
begin
  if biowanze.role_courant() is null then raise exception 'compte non validé'; end if;
  update biowanze.messages m set efface_le = now(), efface_par = t
   where m.id = p_id and m.efface_le is null
     and (m.auteur = t or biowanze.role_courant() = 'rh');
  if not found then raise exception 'message introuvable, ou pas le vôtre'; end if;
end $$;
revoke all on function public.biowanze_effacer_message(bigint) from public, anon;
grant execute on function public.biowanze_effacer_message(bigint) to authenticated;
