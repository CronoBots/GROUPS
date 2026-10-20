-- BIOWANZE, étape 2 : le robot recopie l'horaire installé dans la base.
-- Pendant la saisie en parallèle, le classeur reste la source : une journée
-- venue du classeur se remplace à chaque synchronisation ; une journée
-- SAISIE dans l'application n'est jamais écrasée.
-- La clé est celle que le robot a déjà pour les notifications (secret
-- PUSH_CLE) : seule son empreinte est ici.
create table if not exists biowanze.synchros (
  annee int primary key, maj text, quand timestamptz not null default now(),
  personnes int, journees int
);
alter table biowanze.synchros enable row level security;

create or replace function biowanze.cle_robot(p_cle text) returns boolean
language sql immutable set search_path = '' as $$
  select encode(extensions.digest(coalesce(p_cle,''),'sha256'),'hex')
       = '292e079ae143e8da9c64d3320047ffd15cd9fe2de9a4a05a53292257f349ee0c'
$$;
revoke all on function biowanze.cle_robot(text) from public, anon, authenticated;

-- Ce que la base a déjà : la version (maj) de chaque année.
create or replace function public.biowanze_synchro_etat(p_cle text)
returns table (annee int, maj text, quand timestamptz)
language plpgsql security definer set search_path = '' as $$
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  return query select s.annee, s.maj, s.quand from biowanze.synchros s order by 1;
end $$;

-- Un lot de personnes d'une année : [{"t":"GBT","cat":"Shift 5",
-- "d":{"0101":["AM","",""],…}}, …]. p_fin=true enregistre la version.
create or replace function public.biowanze_synchro(p_cle text, p_annee int, p_maj text, p_lot jsonb, p_fin boolean default false)
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  x jsonb; pid uuid; n_j int := 0; n_p int := 0; k text; v jsonb; jr date;
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  for x in select * from jsonb_array_elements(coalesce(p_lot,'[]'::jsonb)) loop
    pid := null;
    insert into biowanze.personnes(trigramme, categorie)
      values (x->>'t', x->>'cat')
      on conflict (trigramme) do update set categorie = excluded.categorie, maj_le = now()
        where biowanze.personnes.categorie is distinct from excluded.categorie
      returning id into pid;
    if pid is null then select id into pid from biowanze.personnes where trigramme = x->>'t'; end if;
    n_p := n_p + 1;
    -- une journée que le classeur n'écrit plus se VIDE, sans être effacée
    -- (la ligne vide ne se lit pas) ; une saisie n'est jamais touchée
    update biowanze.journees j set cellule = null, annotation = null, commentaire = null, maj_le = now()
      where j.personne_id = pid and j.source = 'classeur'
        and j.jour between make_date(p_annee,1,1) and make_date(p_annee,12,31)
        and not (x->'d') ? to_char(j.jour,'MMDD');
    for k, v in select * from jsonb_each(coalesce(x->'d','{}'::jsonb)) loop
      begin
        jr := make_date(p_annee, substr(k,1,2)::int, substr(k,3,2)::int);
      exception when others then continue;
      end;
      insert into biowanze.journees(personne_id, jour, cellule, annotation, commentaire, source)
        values (pid, jr, nullif(v->>0,''), nullif(v->>1,''), nullif(v->>2,''), 'classeur')
        on conflict (personne_id, jour) do update
          set cellule = excluded.cellule, annotation = excluded.annotation,
              commentaire = excluded.commentaire, maj_le = now()
          where biowanze.journees.source = 'classeur'
            and (biowanze.journees.cellule, biowanze.journees.annotation, biowanze.journees.commentaire)
                is distinct from (excluded.cellule, excluded.annotation, excluded.commentaire);
      n_j := n_j + 1;
    end loop;
  end loop;
  if p_fin then
    insert into biowanze.synchros(annee, maj, quand) values (p_annee, p_maj, now())
      on conflict (annee) do update set maj = excluded.maj, quand = now();
  end if;
  return jsonb_build_object('personnes', n_p, 'journees', n_j);
end $$;

revoke all on function public.biowanze_synchro_etat(text) from public;
revoke all on function public.biowanze_synchro(text,int,text,jsonb,boolean) from public;
grant execute on function public.biowanze_synchro_etat(text) to anon;
grant execute on function public.biowanze_synchro(text,int,text,jsonb,boolean) to anon;
