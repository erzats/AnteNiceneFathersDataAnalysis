-- Top 15 most-cited books.
SELECT book, COUNT(*) AS citations
FROM bible_references
GROUP BY book
ORDER BY citations DESC
LIMIT 15;

-- Fathers that cite widely but never cite deuterocanonical books.
WITH by_author AS (
    SELECT
        author_id,
        COUNT(DISTINCT book) AS unique_books_total,
        COUNT(DISTINCT CASE WHEN testament_group = 'deuterocanonical' THEN book END) AS unique_deut_books
    FROM bible_references
    GROUP BY author_id
)
SELECT author_id, unique_books_total, unique_deut_books
FROM by_author
WHERE unique_books_total >= 15 AND unique_deut_books = 0
ORDER BY unique_books_total DESC, author_id ASC;

-- Tobit references with provenance.
SELECT author_id, work_id, volume, osis_ref, passage
FROM bible_references
WHERE book = 'Tob'
ORDER BY author_id, work_id, osis_ref;
