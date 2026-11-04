-- UN MESSAGE EFFACÉ NE LAISSE PAS DE TRACE (le client, le 04/11/2026 :
-- « les messages effacés ne doivent pas laisser de traces »).
--
-- Jusqu'ici (base/36), effacer gardait la ligne : l'auteur, l'heure, qui
-- avait effacé, et même le texte, que la lecture masquait seulement. Désormais
-- effacer SUPPRIME la ligne, et la lecture ne rend plus que les messages
-- vivants. Les colonnes efface_le et efface_par restent, vides et inutiles :
-- les retirer serait un « drop » de plus, sans rien gagner.
--
-- Seule trace qui demeure, hors de portée : la sauvegarde quotidienne
-- chiffrée de la base (base/22), qui garde trente jours. Un message effacé
-- y vit encore au plus trente jours, puis disparaît avec elle.
--
-- La signature des deux fonctions ne change pas (même retour) : un simple
-- « create or replace », sans « drop ». Le « delete » des messages déjà
-- effacés demande pourtant une confirmation au serveur (CLAUDE.md, « Une
-- migration de la base ») : ce fichier se colle dans l'éditeur SQL du projet.

-- 1. Les messages déjà effacés disparaissent.
delete from biowanze.messages where efface_le is not null;

-- 2. Lire : les seuls messages vivants (la colonne « efface » reste, toujours
--    fausse, pour que la page déjà installée ne change pas d'appel).
create or replace function public.biowanze_messages(p_apres bigint default null)
returns table (id bigint, auteur text, corps text, cree_le timestamptz, efface boolean)
language plpgsql stable security definer set search_path = '' as $$
begin
  if biowanze.role_courant() is null then raise exception 'compte non validé'; end if;
  return query
    select m.id, m.auteur, m.corps, m.cree_le, false
      from (select x.* from biowanze.messages x
             where x.efface_le is null and (p_apres is null or x.id > p_apres)
             order by x.id desc limit 100) m
     order by m.id;
end $$;
revoke all on function public.biowanze_messages(bigint) from public, anon;
grant execute on function public.biowanze_messages(bigint) to authenticated;

-- 3. Effacer : l'auteur, ou la RH (modération). La ligne est supprimée.
create or replace function public.biowanze_effacer_message(p_id bigint)
returns void language plpgsql security definer set search_path = '' as $$
declare t text := biowanze.ma_trigramme();
begin
  if biowanze.role_courant() is null then raise exception 'compte non validé'; end if;
  delete from biowanze.messages m
   where m.id = p_id
     and (m.auteur = t or biowanze.role_courant() = 'rh');
  if not found then raise exception 'message introuvable, ou pas le vôtre'; end if;
end $$;
revoke all on function public.biowanze_effacer_message(bigint) from public, anon;
grant execute on function public.biowanze_effacer_message(bigint) to authenticated;
