// src/types/index.ts

export interface Seminar {
    seminar_title: string;
    date: string;
    location: string;
    time: string;
    speaker: string;
    affiliation: string;
    department: string;
    series: string;
    abstract: string;
    bio: string;
}

export interface SeminarSeriesData {
    department: string;
    series: string; 
    // The raw JSON entries are missing 'department' and 'series', so we Omit them here
    entries: Omit<Seminar, 'department' | 'series'>[];
}