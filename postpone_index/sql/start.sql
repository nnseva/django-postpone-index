CREATE TABLE IF NOT EXISTS public.postpone_index_postponedsql (
    ts bigint NOT NULL PRIMARY KEY,
    description character varying NOT NULL,
    "sql" text NOT NULL,
    "table" character varying,
    db_index character varying,
    fields character varying,
    "done" boolean NOT NULL DEFAULT FALSE,
    "error" text
);
CREATE INDEX IF NOT EXISTS postpone_index_postponedsql_db_index ON public.postpone_index_postponedsql USING btree (db_index);
CREATE INDEX IF NOT EXISTS postpone_index_postponedsql_db_index_like ON public.postpone_index_postponedsql USING btree (db_index varchar_pattern_ops);
CREATE INDEX IF NOT EXISTS postpone_index_postponedsql_table ON public.postpone_index_postponedsql USING btree ("table");
CREATE INDEX IF NOT EXISTS postpone_index_postponedsql_table_like ON public.postpone_index_postponedsql USING btree ("table" varchar_pattern_ops);
