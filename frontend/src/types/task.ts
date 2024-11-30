export type Task = {
    id: string;
    title: string;
    description: string;
    group: string;
    status: string;
    start_time: Date;
    end_time: Date;
    event_type: string;
  };