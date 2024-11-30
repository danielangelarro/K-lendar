import { useState, useEffect } from "react";
import TableOne from "../components/Tables/TableOne";
import TableTwo from "../components/Tables/TableTwo";
import GroupForm from "../components/Forms/GroupForm";
import api from '../api/axios'; // Asegúrate de importar tu configuración de axios
import { User } from "../types/user";
import { Group } from "../types/group";
import Sucessfully from "../components/Alerts/Sucessfully";

const GroupPage = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [groupes, setGroupes] = useState<Group[]>([]);
    const [groupSelected, setGroupSelected] = useState<Group | null>(null);
    const [userModal, setUserModal] = useState<boolean>(false);
    const [modal, setModal] = useState<boolean>(false);
    const [createEdit, setCreateEdit] = useState<boolean>(false);
    const [modalSuccessfully, setModalSuccessfully] = useState<boolean>(false);
    const [msgSuccessfully, setMsgSuccessfully] = useState<string>('');

    useEffect(() => {
        // Cargar usuarios y grupos al montar el componente
        fetchGroups();
        // fetchUsers();
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

    const fetchUsers = async () => {
        try {
            const response = await api.get('/users');
            setUsers(response.data);
        } catch (error) {
            console.error('Error al obtener usuarios:', error);
        }
    };

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
            setCreateEdit(true);
            setModal(true);
        }
    };

    const vueUsersOfGroup = (id: string) => {
        const group = groupes.find(group => group.id === id);
        if (group) {
            setGroupSelected(group);
            setUserModal(true);
        }
    };

    const delUserOfGroup = (id: string) => {
        // Implementar lógica para eliminar usuario del grupo
        // const updatedMembers = groupSelected?.members.filter(userId => userId !== id);
        // if (updatedMembers) {
        //     setGroupSelected(updatedMembers);
        // }
    };

    const endEditGroup = async (group: Group) => {
        try {
            if (group.id) {
                // Editar grupo existente
                const response = await api.put(`/groups/${group.id}`, group); // Cambia la URL según tu API
                setGroupes(groupes.map(g => (g.id === group.id ? response.data : g)));
            } else {
                // Crear nuevo grupo
                const response = await api.post('/groups', group); // Cambia la URL según tu API
                setGroupes([...groupes, response.data]);
            }
            setModal(false);
        } catch (error) {
            console.error('Error al guardar grupo:', error);
        }
    };

    const clickCreate = () => {
        setCreateEdit(false);
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

            {/* {userModal && groupSelected && (
                <TableOne back={setUserModal} userData={users.filter(user => groupSelected.members.includes(user.id))} del={delUserOfGroup} />
            )}  */}
            {modal && (
                <GroupForm create_edit={createEdit} edit={endEditGroup} old_group={groupSelected} header={createEdit ? "Edit Group" : "Create Group"} />
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