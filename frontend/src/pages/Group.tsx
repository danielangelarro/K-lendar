import { useState, useEffect } from "react";
import TableOne from "../components/Tables/TableOne";
import TableTwo from "../components/Tables/TableTwo";
import GroupForm from "../components/Forms/GroupForm";
import AssignParentGroupForm from "../components/Forms/AssignParentGroupForm";
import api from '../api/axios';
import { User } from "../types/user";
import { Group } from "../types/group";
import Sucessfully from "../components/Alerts/Sucessfully";

const GroupPage = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [groupes, setGroupes] = useState<Group[]>([]);
    const [groupSelected, setGroupSelected] = useState<Group | null>(null);
    const [userModal, setUserModal] = useState<boolean>(false);
    const [modal, setModal] = useState<boolean>(false);
    const [modalSuccessfully, setModalSuccessfully] = useState<boolean>(false);
    const [msgSuccessfully, setMsgSuccessfully] = useState<string>('');

    useEffect(() => {
        // Cargar usuarios y grupos al montar el componente
        fetchGroups();
    }, []);

    useEffect(() => {
        if (modal) setUserModal(false);
    }, [modal]);

    useEffect(() => {
        if (userModal) setModal(false);
    }, [userModal]);

    // Efecto para manejar el mensaje de éxito
    useEffect(() => {
      if (modalSuccessfully) setTimeout(() => setModalSuccessfully(false), 1500);
    }, [modalSuccessfully]);

    const fetchGroups = async () => {
        try {
            const response = await api.get('/groups/all');
            setGroupes(response.data);
        } catch (error) {
            console.error('Error al obtener grupos:', error);
        }
    };

    const del = async (id: string) => {
      try {
        await api.delete(`/groups/${id}`);
        
        // Actualizar estado local
        const new_groups = groupes.filter(group => group.id !== id);
        setGroupes(new_groups);
  
        // Mostrar mensaje de éxito
        setMsgSuccessfully("Grupo eliminado exitosamente");
        setModalSuccessfully(true);
      } catch (error) {
        console.error('Error al eliminar grupo:', error);
        setMsgSuccessfully("Error al eliminar grupo");
        setModalSuccessfully(true);
      }
    };

    const startEditGroup = (id: string) => {
        const group = groupes.find(group => group.id === id);
        if (group) {
            setGroupSelected(group);
            setModal(true);
        }
    };

    const vueUsersOfGroup = async (id: string) => {
        const group = groupes.find(group => group.id === id);
        if (group) {
            const response = await api.get(`/groups/${id}/members`);
            setUsers(response.data);

            setGroupSelected(group);
            setUserModal(true);
        }
    };

    const delUserOfGroup = async (group_id: string, user_id: string) => {
        try {
            await api.delete(`/groups/${group_id}/${user_id}/remove_member`);

            setMsgSuccessfully("User removed successfully.");
        } catch (error) {
            console.log('Error al eliminar usuario', error);
            setMsgSuccessfully("Error");
        }
    };

    const endEditGroup = async (group: Group) => {
        try {
            if (group.id) {
                const response = await api.put(`/groups/${group.id}`, group);
                setGroupes(groupes.map(g => (g.id === group.id ? response.data : g)));
            } else {
                const response = await api.post('/groups', group);
                setGroupes([...groupes, response.data]);
            }
            setModal(false);
        } catch (error) {
            console.error('Error al guardar grupo:', error);
        }
    };

    const clickCreate = () => {
        setGroupSelected(null);
        setModal(true);
    };

    return (
        <>
            {modalSuccessfully && (
              <div className=''>
                <Sucessfully msg={msgSuccessfully}/>
              </div>
            )}

            {userModal && groupSelected && (
                <TableOne back={setUserModal} userData={users} del={delUserOfGroup} groupId={groupSelected.id} is_owner={groupSelected.is_my}/>
            )} 
            {modal && (
                <GroupForm set={setModal} edit={endEditGroup} old_group={groupSelected} header={groupSelected ? "Edit Group" : "Create Group"} />
            )}
            {!(userModal || modal) && (
                <>
                    <TableTwo groupes={groupes} edit={startEditGroup} del={del} vueUsersOfGroup={vueUsersOfGroup} />
                    <button onClick={clickCreate} className="flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90">
                        New Group
                    </button>
                </>
            )}
        </>
    );
}

export default GroupPage;