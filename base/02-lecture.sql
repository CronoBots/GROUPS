-- BIOWANZE, étape 2 : ce que l'application lit. Tout passe par des
-- fonctions public.biowanze_* : seul un utilisateur CONNECTÉ et RATTACHÉ à
-- un compte BIOWANZE obtient quelque chose. Tout le monde lit l'horaire de
-- tout le monde, comme le classeur aujourd'hui (le client, le 20/10/2026 :
-- « tout le monde utilise actuellement le fichier pour connaître son
-- horaire »).

-- Qui suis-je : mon rôle et ma personne.
create or replace function public.biowanze_moi()
returns table (role text, trigramme text, nom text, prenom text, categorie text, statut text)
language sql stable security definer set search_path = '' as $$
  select c.role::text, p.trigramme, p.nom, p.prenom, p.categorie, p.statut
  from biowanze.comptes c left join biowanze.personnes p on p.id = c.personne_id
  where c.user_id = auth.uid()
$$;

-- Les personnes actives.
create or replace function public.biowanze_personnes()
returns table (trigramme text, nom text, prenom text, categorie text, statut text)
language sql stable security definer set search_path = '' as $$
  select p.trigramme, p.nom, p.prenom, p.categorie, p.statut
  from biowanze.personnes p
  where p.actif and biowanze.role_courant() is not null
  order by p.trigramme
$$;

-- Les journées d'une période, toutes personnes.
create or replace function public.biowanze_journees(p_du date, p_au date)
returns table (trigramme text, jour date, cellule text, annotation text, commentaire text, source text, maj_le timestamptz)
language sql stable security definer set search_path = '' as $$
  select p.trigramme, j.jour, j.cellule, j.annotation, j.commentaire, j.source, j.maj_le
  from biowanze.journees j join biowanze.personnes p on p.id = j.personne_id
  where biowanze.role_courant() is not null
    and j.jour between p_du and p_au
    and p_au - p_du <= 400
    and (j.cellule is not null or j.annotation is not null or j.commentaire is not null)
  order by p.trigramme, j.jour
$$;

-- Ni le public ni n'importe quel compte de PINO : seuls les comptes
-- connectés peuvent appeler, et la fonction vérifie ensuite le rattachement.
revoke all on function public.biowanze_moi() from public, anon;
revoke all on function public.biowanze_personnes() from public, anon;
revoke all on function public.biowanze_journees(date, date) from public, anon;
grant execute on function public.biowanze_moi() to authenticated;
grant execute on function public.biowanze_personnes() to authenticated;
grant execute on function public.biowanze_journees(date, date) to authenticated;
