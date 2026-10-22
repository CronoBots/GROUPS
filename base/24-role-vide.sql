-- UN COMPTE SANS RÔLE N'EST PAS UN CONTREMAÎTRE (22/10/2026, trouvé en
-- éprouvant base/23). biowanze.role_courant() est NULL pour un compte
-- connecté mais pas encore validé ; « NULL not in ('rh','hierarchie') »
-- vaut NULL, et le « if … then raise » ne levait rien : saisir une
-- journée, annuler une saisie, viser ou décider une demande restaient
-- ouverts à tout compte connecté non validé. La garde devient « rôle vide
-- OU hors de la liste », dans les quatre fonctions, par la même
-- substitution mécanique (biowanze_contresigner_recyclage avait déjà un
-- coalesce). La substitution est rejouable : elle ne trouve plus rien la
-- seconde fois.
do $$
declare f text; def text; neu text;
begin
  foreach f in array array['public.biowanze_saisir','public.biowanze_annuler_saisie',
                           'public.biowanze_viser_demande','public.biowanze_decider_demande'] loop
    select pg_get_functiondef(p.oid) into def from pg_proc p where p.oid = (
      select p2.oid from pg_proc p2 join pg_namespace n on n.oid = p2.pronamespace
       where n.nspname||'.'||p2.proname = f limit 1);
    neu := regexp_replace(def, 'if biowanze\.role_courant\(\) not in \(', 'if biowanze.role_courant() is null or biowanze.role_courant() not in (', 'g');
    neu := regexp_replace(neu, 'if moi not in \(', 'if moi is null or moi not in (', 'g');
    if neu <> def then execute neu; end if;
  end loop;
end $$;
