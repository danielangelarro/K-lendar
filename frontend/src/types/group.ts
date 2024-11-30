export type Group = {
    id: number;
    name: string;
    description: string;
    is_hierarchical: boolean;
    owler: number,
    members: number[]
}