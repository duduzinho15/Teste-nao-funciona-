-- Script para adicionar a restrição UNIQUE à coluna 'nome' da tabela 'clubes'
-- Verifica se a restrição já existe antes de tentar adicioná-la
DO $$
BEGIN
    -- Verifica se a restrição já existe
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'clubes'
        AND constraint_name = 'uq_clubes_nome'
        AND constraint_type = 'UNIQUE'
    ) THEN
        -- Adiciona a restrição UNIQUE
        EXECUTE 'ALTER TABLE clubes ADD CONSTRAINT uq_clubes_nome UNIQUE (nome)';
        RAISE NOTICE 'Restrição UNIQUE adicionada com sucesso à coluna nome da tabela clubes.';
    ELSE
        RAISE NOTICE 'A restrição UNIQUE já existe na coluna nome da tabela clubes.';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'Erro ao adicionar a restrição UNIQUE: %', SQLERRM;
END $$;
