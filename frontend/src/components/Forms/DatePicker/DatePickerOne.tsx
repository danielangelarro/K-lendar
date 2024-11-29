type props = {
  date: string;
  set: React.Dispatch<React.SetStateAction<Date>>;
}
const DatePickerOne = ({date, set}: props) => {

  return (
    <div>
      <div className="relative">
        <input
          className="w-full rounded border-[1.5px] border-stroke bg-transparent px-5 py-3 font-normal outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
          type="datetime-local"
          value={date}
          onChange={(e) => set(new Date(e.target.value))}
        />
      </div>
    </div>
  );
};

export default DatePickerOne;
