export interface Summary {
  total_references: number;
  by_testament: {
    new_testament: number;
    old_testament_or_other: number;
    deuterocanonical: number;
  };
  unique_authors: number;
  unique_books: number;
  top_books: { book: string; display_name: string; count: number }[];
  top_authors: { author_id: string; display_name: string; count: number }[];
  unquoted_books: { book: string; display_name: string }[];
}

export interface BookRow {
  book: string;
  display_name: string;
  testament_group: "new_testament" | "old_testament_or_other" | "deuterocanonical";
  total_count: number;
  volume_counts: Record<string, number>;
}

export interface AuthorRow {
  author_id: string;
  display_name: string;
  floruit: number | null;
  century: number | null;
  is_editor: boolean;
  total_citations: number;
  unique_books: number;
  deuterocanonical_books_cited: number;
  quoted_deuterocanonical: boolean;
  top_books: { book: string; display_name: string; count: number }[];
}

export interface PsalmRow {
  psalm: string;
  count: number;
}

export interface VolumeComparisonRow {
  book: string;
  display_name: string;
  testament_group: string;
  total_count: number;
  by_volume: Record<string, number>;
}
