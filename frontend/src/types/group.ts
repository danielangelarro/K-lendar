export type Group = {
    id: string;
    name: string;
    description: string;
    parent: string,
    cant_members: number;
    owner_username: string,
    is_my: boolean,
}