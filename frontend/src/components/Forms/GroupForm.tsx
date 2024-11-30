import { useState } from "react";
import { Group } from "../../types/group";
import CheckboxTwo from "../Checkboxes/CheckboxTwo";

type props = {
  edit: any;
  header: string;
  old_group: Group;
  create_edit: boolean;
}

const GroupForm = ({old_group, header, edit, create_edit}: props) => {
  const [ name, setName ] = useState<string>(create_edit ? old_group.name : '')
  const [ description, setDescription ] = useState<string>(create_edit ? old_group.description : '')
  const [ hierarchical, setHierarchical ] = useState<boolean>(create_edit ? old_group.is_hierarchical : false)

  function create() {
    const group = {
      id: create_edit ? old_group.id : -1,
      name: name,
      description: description,
    }

    edit(group)
  }

  return (
      <div className="gap-9">
      <div className="flex flex-col gap-9">
        {/* <!-- Contact Form --> */}
        <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
          <div className="border-b border-stroke py-4 px-6.5 dark:border-strokedark">
            <h3 className="font-medium text-black dark:text-white">
              {header}
            </h3>
          </div>
          <form action="#">
            <div className="p-6.5">
              <div className="mb-4.5 flex flex-col gap-6 xl:flex-row">
                <div className="w-full xl:w-1/2">
                  <label className="mb-2.5 block text-black dark:text-white">
                    Name
                  </label>
                  <input
                    type="text"
                    placeholder="Title"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full rounded border-[1.5px] border-stroke bg-transparent py-3 px-5 text-black outline-none transition focus:border-primary active:border-primary disabled:cursor-default disabled:bg-whiter dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                  />
                </div>
              </div>
              <div className="mb-6">
                <label className="mb-2.5 block text-black dark:text-white">
                  Description
                </label>
                <textarea
                  rows={4}
                  placeholder="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full rounded border-[1.5px] border-stroke bg-transparent py-3 px-5 text-black outline-none transition focus:border-primary active:border-primary disabled:cursor-default disabled:bg-whiter dark:border-form-strokedark dark:bg-form-input dark:text-white dark:focus:border-primary"
                ></textarea>
              </div>
              <div className="mb-6">
                <CheckboxTwo text="Hierarchical" value={hierarchical} set={setHierarchical}/>
              </div>
              
              <button onClick={() => create()} className="flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90">
                {header}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default GroupForm;