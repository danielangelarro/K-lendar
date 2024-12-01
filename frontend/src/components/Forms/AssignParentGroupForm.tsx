import React, { useEffect, useState } from 'react';
import { Group } from '../../types/group';
import api from '../../api/axios';

interface AssignParentGroupFormProps {
  currentGroupId: Group | null; 
  set: (value: boolean) => void;
}

const AssignParentGroupForm: React.FC<AssignParentGroupFormProps> = ({ currentGroupId, set }) => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedParentGroupId, setSelectedParentGroupId] = useState<string | null>(null);

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await api.get('/groups/all'); // Obtener todos los grupos
        setGroups(response.data);
      } catch (error) {
        console.error('Error al obtener grupos:', error);
      }
    };

    fetchGroups();
  }, []);

  const handleAssignParentGroup = async () => {
    try {
      await api.put(`/groups/parent/${currentGroupId!.id}/${selectedParentGroupId}`);
      set(false);
    } catch (error) {
      console.error('Error al asignar grupo padre:', error);
    }
  };

  return (
    <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark p-6">
      <h3 className="font-medium text-black dark:text-white">Assign Parent Group</h3>
      <div className="mb-4">
        <label className="mb-2 block text-black dark:text-white">Select Parent Group:</label>
        <select
          value={selectedParentGroupId || ''}
          onChange={(e) => setSelectedParentGroupId(e.target.value || null)}
          className="w-full rounded border-[1.5px] border-stroke bg-transparent py-3 px-5 text-black outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white"
        >
          <option value="">None</option>
          {groups.map(group => (
            <option key={group.id} value={group.id}>{group.name}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 w-full justify-center rounded p-3">
        <button onClick={() => handleAssignParentGroup()} className="flex justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90 m-5">
          Asign
        </button>
        <button onClick={() => set(false)} className="flex justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90 m-5">
          Cancel
        </button>
      </div>
    </div>
  );
};

export default AssignParentGroupForm;
