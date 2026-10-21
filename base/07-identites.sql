-- Le nom, le prénom et le matricule de chacun (étape 2 ; le client, le
-- 20/10/2026, à « l'informatique et la protection des données acceptent-elles
-- les noms et matricules dans la base ? » : « oui »).
--
-- Le robot les lit dans le classeur (onglet « Polyvalence » ; à défaut, la
-- ligne des noms, « Nom P. ») par convertir-horaire.py --identites, HORS du
-- dépôt, et les envoie ici avec sa clé. Le dépôt public n'en voit jamais
-- rien. Le matricule n'est rendu par AUCUNE fonction de lecture : il dort
-- dans la base pour l'export et la RH, plus tard.
--
-- p_lot : {"GBT": {"nom": "…", "prenom": "…", "matricule": "…"}, …}
create or replace function public.biowanze_identites(p_cle text, p_lot jsonb)
returns int
language plpgsql security definer set search_path = '' as $$
declare k text; v jsonb; n int := 0; m int;
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  for k, v in select * from jsonb_each(coalesce(p_lot, '{}'::jsonb)) loop
    update biowanze.personnes
       set nom = nullif(v->>'nom', ''), prenom = nullif(v->>'prenom', ''),
           matricule = nullif(v->>'matricule', ''), maj_le = now()
     where trigramme = k
       and (nom, prenom, matricule) is distinct from
           (nullif(v->>'nom', ''), nullif(v->>'prenom', ''), nullif(v->>'matricule', ''));
    get diagnostics m = row_count;
    n := n + m;
  end loop;
  return n;
end $$;
revoke all on function public.biowanze_identites(text, jsonb) from public;
grant execute on function public.biowanze_identites(text, jsonb) to anon;

-- La liste des comptes de la RH, avec le nom : une demande « ABC » seule se
-- valide mal (remplace biowanze_comptes dans l'application ; le type de
-- retour change, d'où une fonction nouvelle plutôt qu'un remplacement).
create or replace function public.biowanze_comptes_rh()
returns table (user_id uuid, email text, trigramme text, nom text, prenom text, categorie text, role text, valide boolean, cree_le timestamptz)
language sql stable security definer set search_path = '' as $$
  select c.user_id, c.email, p.trigramme, p.nom, p.prenom, p.categorie, c.role::text, c.valide, c.cree_le
  from biowanze.comptes c left join biowanze.personnes p on p.id = c.personne_id
  where biowanze.role_courant() = 'rh'
  order by c.valide, c.cree_le desc
$$;
revoke all on function public.biowanze_comptes_rh() from public, anon;
grant execute on function public.biowanze_comptes_rh() to authenticated;
