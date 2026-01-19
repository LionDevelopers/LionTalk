export interface Seminar {
    seminar_title: string;
    date: string
    location: string;
    time: string;
    speaker: string;
    affiliation: string;
    abstract: string;
    bio: string;
}

export interface SeminarData {
    entries: Seminar[];
}
