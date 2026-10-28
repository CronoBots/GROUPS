-- L'EFFACEMENT DÉFINITIF DES DEMANDES SUPPRIMÉES (le client, le 28/10/2026 :
-- « oui effacement définitif ok »). C'est la partie de 16-effacer.sql restée
-- en attente le 22/10, relue sur l'état RÉEL de la base avant d'être écrite :
--
--  - biowanze_modifier_demande, depuis 13-modifier.sql, note « Remplacée par
--    la demande n° … » sur TOUTE demande modifiée, signée ou non. La purge
--    de 16 gardait toutes celles-là ; elle ne garde ici que celles qu'un
--    remplaçant avait déjà signées (accords), seules à devoir rester (25).
--  - Les notifications déjà ENVOYÉES d'une demande effacée s'effacent aussi
--    (leur titre et leur texte décrivent la demande) ; aucune clé étrangère
--    n'y pointe, seul le robot les lit (notifs_a_envoyer, non envoyées).
--  - La table biowanze.historique garde la trace de chaque effacement
--    (déclencheur « tracer », 01-fondations.sql), comme prévu en 16.
--
-- Contient des delete : le serveur de Supabase demande une confirmation que
-- le mode « Auto » ne donne pas. À coller dans l'éditeur SQL du projet.

-- 1. Supprimer sa demande l'efface (même garde qu'avant : personne d'autre
--    n'a signé).
create or replace function public.biowanze_annuler_demande(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
declare d record;
begin
  select * into d from biowanze.demandes where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente' for update;
  if not found then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.valide_cm is not null or d.valide_rh is not null or coalesce(d.accords,'{}'::jsonb) <> '{}'::jsonb then
    raise exception 'déjà signée par une autre personne : elle ne se supprime plus';
  end if;
  delete from biowanze.notifs where demande_id = p_id;
  delete from biowanze.demandes where id = p_id;
  return 'effacee';
end $$;

-- 2. Modifier sa demande efface l'ancienne, sauf si un remplaçant l'avait
--    déjà signée : elle reste alors annulée, remplacée par la nouvelle (25).
create or replace function public.biowanze_modifier_demande(p_id bigint, p_formulaire text, p_lignes jsonb, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); d record; nid bigint;
begin
  if pid is null then raise exception 'compte non validé'; end if;
  select * into d from biowanze.demandes where id = p_id and personne_id = pid for update;
  if not found or d.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.valide_cm is not null or d.valide_rh is not null then
    raise exception 'déjà visée : elle ne se modifie plus ; annulez-la et faites-en une nouvelle';
  end if;
  delete from biowanze.notifs where demande_id = p_id and envoye_le is null;
  if coalesce(d.accords,'{}'::jsonb) <> '{}'::jsonb then
    update biowanze.demandes set statut = 'annulee' where id = p_id;
    nid := public.biowanze_demander_formulaire(p_formulaire, p_lignes, p_texte);
    update biowanze.demandes set motif_refus = 'Remplacée par la demande n° '||nid where id = p_id;
    return nid;
  end if;
  delete from biowanze.notifs where demande_id = p_id;
  delete from biowanze.demandes where id = p_id;
  nid := public.biowanze_demander_formulaire(p_formulaire, p_lignes, p_texte);
  return nid;
end $$;

-- 3. Supprimer sa fiche de recyclage l'efface.
create or replace function public.biowanze_annuler_recyclage(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
begin
  delete from biowanze.recyclages_fiches
   where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente';
  if not found then raise exception 'fiche introuvable ou déjà traitée'; end if;
  return 'effacee';
end $$;

-- 4. Les demandes et fiches déjà annulées (mesuré le 28/10/2026 : 8 demandes,
--    aucune signée par un remplaçant, leurs 8 notifications envoyées, et
--    4 fiches de recyclage).
delete from biowanze.notifs where demande_id in (
  select id from biowanze.demandes
   where statut = 'annulee' and coalesce(accords,'{}'::jsonb) = '{}'::jsonb);
delete from biowanze.demandes
 where statut = 'annulee' and coalesce(accords,'{}'::jsonb) = '{}'::jsonb;
delete from biowanze.recyclages_fiches where statut = 'annulee';

-- Ce qui reste d'annulé (attendu : 0 et 0)
select (select count(*) from biowanze.demandes where statut = 'annulee') as demandes_annulees_restantes,
       (select count(*) from biowanze.recyclages_fiches where statut = 'annulee') as fiches_annulees_restantes;
