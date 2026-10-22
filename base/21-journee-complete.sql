-- L'HEURE DE DÉPART OU D'ARRIVÉE SEULEMENT POUR UNE JOURNÉE INCOMPLÈTE (le
-- client, le 22/10/2026 : « la justification arrivée ou départ plus tôt ou
-- plus tard n'est logique que si la personne ne prend pas une journée
-- complète, c'est-à-dire 8 heures »).
--
-- La durée d'un code : ses heures quand il se compte en heures (la valeur
-- absolue : une reprise de flex time s'écrit « -4 ») ; une journée (8 h)
-- sinon. Une ligne refuse :
--   un second type quand le premier fait déjà 8 h ou plus ;
--   une heure de départ ou d'arrivée quand le total fait 8 h ou plus.
create or replace function biowanze.duree_code(p text)
returns numeric language sql stable security definer set search_path = '' as $$
  select coalesce((select case when c.unite = 'h' and c.heures is not null then abs(c.heures) else 8 end
                     from biowanze.codes c where c.code = p), 8)
$$;
revoke all on function biowanze.duree_code(text) from public, anon, authenticated;

create or replace function biowanze.demande_ligne_garde()
returns trigger language plpgsql security definer set search_path = '' as $$
declare l jsonb; d1 numeric; d2 numeric;
begin
  for l in select * from jsonb_array_elements(coalesce(new.lignes,'[]'::jsonb)) loop
    if l ? 'code' and (l ? 'code2' or l ? 'part') then
      d1 := biowanze.duree_code(l->>'code');
      d2 := case when l ? 'code2' then biowanze.duree_code(l->>'code2') else 0 end;
      if l ? 'code2' and d1 >= 8 then
        raise exception 'le % : % couvre déjà la journée, pas de second type', to_char((l->>'j')::date,'DD/MM'), l->>'code';
      end if;
      if l ? 'part' and d1 + d2 >= 8 then
        raise exception 'le % : journée complète (8 h), pas d''heure de départ ou d''arrivée', to_char((l->>'j')::date,'DD/MM');
      end if;
    end if;
  end loop;
  return new;
end $$;

create or replace trigger demande_ligne_garde before insert or update of lignes on biowanze.demandes
  for each row execute function biowanze.demande_ligne_garde();
