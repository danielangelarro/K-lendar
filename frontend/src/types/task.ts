export type Task = {
    id: string;
    title: string;
    description: string;
    group: any;
    status: string;
    start_time: Date;
    end_time: Date;
    event_type: string;
  };