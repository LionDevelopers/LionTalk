// src/types/index.ts

export interface Seminar {
    seminar_title: string;
    date: string;
    location: string;
    time: string;
    speaker: string;
    affiliation: string;
    department: string;
    abstract: string;
    bio: string;
}

// New interface for the grouped structure in seminars.json
export interface DepartmentData {
    department: string;
    // The JSON entries are missing the 'department' field, so we Omit it here
    entries: Omit<Seminar, 'department'>[];
}