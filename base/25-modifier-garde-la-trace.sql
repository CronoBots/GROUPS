-- À APPLIQUER : le connecteur demande une confirmation (le corps contient « delete ») ;
-- pas appliquée le 23/10/2026, en attente de l'accord du client.
-- MODIFIER UNE DEMANDE DÉJÀ SIGNÉE PAR LE REMPLAÇANT (23/10/2026, en
-- répondant au client : « quelle est la règle pour la modification ? »).
--
-- La règle : le demandeur modifie sa demande tant que le contremaître de
-- pause ne l'a pas acceptée (ni la RH) ; la modification fait une
-- NOUVELLE feuille, que le remplaçant signe à nouveau.
--
-- Le défaut corrigé : base/16 effaçait l'ancienne feuille dans tous les
-- cas, alors que base/13 la gardait « annulée, remplacée par la demande
-- n° N ». Une feuille qu'un remplaçant a signée ne s'efface plus : elle
-- reste dans l'historique, annulée, avec le numéro de celle qui la
-- remplace (la règle de la suppression, base/16, est la même : signée par
-- un autre, elle ne disparaît plus). Non signée, elle s'efface comme avant.
create or replace function public.biowanze_modifier_demande(p_id bigint, p_formulaire text, p_lignes jsonb, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); d record; nid bigint; signee boolean;
begin
  if pid is null then raise exception 'compte non validé'; end if;
  select * into d from biowanze.demandes where id = p_id and personne_id = pid for update;
  if not found or d.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.valide_cm is not null or d.valide_rh is not null then
    raise exception 'déjà acceptée par le contremaître : elle ne se modifie plus';
  end if;
  signee := d.accords is not null and d.accords <> '{}'::jsonb;
  delete from biowanze.notifs where demande_id = p_id and envoye_le is null;
  if signee then
    update biowanze.demandes set statut = 'annulee' where id = p_id;
  else
    delete from biowanze.demandes where id = p_id;
  end if;
  nid := public.biowanze_demander_formulaire(p_formulaire, p_lignes, p_texte);
  if signee then
    update biowanze.demandes set motif_refus = 'Remplacée par la demande n° '||nid where id = p_id;
  end if;
  return nid;
end $$;
