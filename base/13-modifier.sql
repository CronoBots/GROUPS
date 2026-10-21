-- MODIFIER SA DEMANDE (le client, le 22/10/2026 : « les demandes de congé
-- doivent être accessibles aux opérateurs, modifiables, et voir
-- l'avancement de la validation, avec un historique de leurs demandes »).
--
-- Tant que ni le contremaître ni la RH ne l'a visée, le demandeur peut
-- refaire sa demande. On ne réécrit pas la ligne : l'ancienne passe
-- « annulée » avec la mention « Remplacée par la demande n° N », et la
-- nouvelle est créée par biowanze_demander_formulaire, avec TOUTES ses
-- vérifications (aucune règle recopiée ici, qui divergerait). Le tout dans
-- une seule transaction : si la nouvelle est refusée, l'ancienne reste
-- en attente, intacte. L'historique garde les deux ; l'accord déjà donné
-- par un remplaçant ne passe pas à la nouvelle : il la signe à nouveau.

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
  update biowanze.demandes set statut = 'annulee' where id = p_id;
  nid := public.biowanze_demander_formulaire(p_formulaire, p_lignes, p_texte);
  update biowanze.demandes set motif_refus = 'Remplacée par la demande n° '||nid where id = p_id;
  return nid;
end $$;

revoke all on function public.biowanze_modifier_demande(bigint,text,jsonb,text) from public, anon;
grant execute on function public.biowanze_modifier_demande(bigint,text,jsonb,text) to authenticated;
