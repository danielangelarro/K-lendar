import { useState, useEffect } from "react";
import TableOne from "../components/Tables/TableOne";
import TableTwo from "../components/Tables/TableTwo";
import GroupForm from "../components/Forms/GroupForm";

import { User } from "../types/user";
import { Group } from "../types/group";

const userData: User[] = [
    {
      id: 0,
      username: 'Paco',
      email: 'Paco@random.com',
    },
    {
      id: 1,
      username: 'Carla',
      email: 'Carla@random.com',
    },
    {
      id: 2,
      username: 'Juan',
      email: 'Juan@random.com',
    },
    {
      id: 3,
      username: 'Petter',
      email: 'Petter@random.com',
    },
    {
      id: 4,
      username: 'Ana',
      email: 'Ana@random.com',
    },
  ];

  const groupData: Group[] = [
    {
      id: 0,
      name: 'jefatura',
      description: 'Apple Watch Series 7',
      owler: 0,
      members: [0,1,2],
      is_hierarchical: true,
    },
    {
      id: 1,
      name: 'sector 1',
      description: 'Dell Inspiron 15',
      owler: 1,
      members: [1,3],
      is_hierarchical: false,
    },
    {
      id: 2,
      name: 'sector 2',
      description: 'HP Probook 450',
      owler: 2,
      members: [2,4],
      is_hierarchical: false,
    },
  ];

const GroupPage = () => {
    const [ users, setUsers ] = useState<User[]>(userData)
    const [ groupes, setGroupes ] = useState<Group[]>(groupData)
    const [ groupSelected, setGroupSelected ] = useState<Group>(groupData[0])
    const [ userModal, setUserModal ] = useState<boolean>(false)
    const [ modal, setModal ] = useState<boolean>(false)
    const [ createEdit, setCreateEdit ] = useState<boolean>(false)

    useEffect(() => {
      if (modal) setUserModal(false)
    },[modal])

    useEffect(() => {
      if (userModal) setModal(false)
    },[userModal])

    function startEditGroup(id: number) {
      setGroupSelected(groupes.filter(group => group.id == id)[0])
      setCreateEdit(true)
      setModal(true)
    }

    function vueUsersOfGroup(id: number) {
      setGroupSelected(groupes.filter(group => group.id == id)[0])
      setUserModal(true)
    }

    function delUserOfGroup(id: number) {
      groupSelected.members.filter(users => users != id)
    }

    function endEditGroup(group: Group) {
      console.log('hacer peticion')
    
      if (group.id >= 0) {
        const old_group = groupes.filter(_group_ => _group_.id == group.id)[0]
        old_group.name = group.name
        old_group.description = group.description
        old_group.is_hierarchical = group.is_hierarchical
      }
  
      else {
        groupes.push({
          id: groupes.length,
          name: group.name,
          description: group.description,
          is_hierarchical: group.is_hierarchical,
          members: [],
          owler: 0,
        })
      }
  
      setModal(false)
    }

    function clickCreate() {
      setCreateEdit(false)
      setModal(true)
      console.log(modal)
    }

    return (
        <>
            {userModal && groupSelected && (
              <TableOne back={setUserModal} userData={users.filter(user => user.id in groupSelected.members)} del={delUserOfGroup}/>
            )}
            {modal && groupSelected && (
              <GroupForm create_edit={createEdit} edit={endEditGroup} old_group={groupSelected} header={createEdit ? "Edit Group" : "Create Group"} />
            )}
            {!(userModal || modal) && (
              <>
                <TableTwo groupData={groupes} edit={startEditGroup} vueUsersOfGroup={vueUsersOfGroup} />
                <button onClick={() => clickCreate()} className="flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90">
                  New Group
                </button>
              </>
            )}
        </>
    )
}

export default GroupPage;