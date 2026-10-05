export type AuthUser = {
  email: string;
  name: string;
  role: "hr_manager" | "hr";
};

export type Country = {
  code: string;
  name: string;
  currency_code: string;
};

export type JobTitle = {
  id: number;
  name: string;
};

export type Employee = {
  id: number;
  employee_code: string;
  full_name: string;
  country: Country;
  job_title: JobTitle;
  salary: string;
  department: string;
  employment_status: string;
  hired_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ReferenceData = {
  countries: Country[];
  job_titles: JobTitle[];
  employment_statuses: string[];
};

export type EmployeeList = {
  items: Employee[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type EmployeeInput = {
  employee_code: string;
  full_name: string;
  job_title_id: number;
  country_code: string;
  salary: string;
  department: string;
  employment_status: string;
  hired_at: string | null;
};

export type CountryInsight = {
  country: Country;
  employee_count: number;
  min_salary: string | null;
  max_salary: string | null;
  average_salary: string | null;
  total_payroll: string;
  highest_paid_employee: Pick<Employee, "id" | "employee_code" | "full_name" | "salary"> | null;
  lowest_paid_employee: Pick<Employee, "id" | "employee_code" | "full_name" | "salary"> | null;
  job_titles: Array<{
    job_title: JobTitle;
    employee_count: number;
    average_salary: string | null;
  }>;
};

export type EmployeeExportStatus = "queued" | "processing" | "sent" | "failed";

export type EmployeeExportJob = {
  id: string;
  status: EmployeeExportStatus;
  recipient_email: string;
  filters: {
    search: string | null;
    country_code: string | null;
    job_title_id: number | null;
    sort_by: "full_name" | "salary" | "hired_at" | "updated_at" | "employee_code";
    sort_dir: "asc" | "desc";
  };
  row_count: number | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type EmployeeExportInput = {
  recipient_email: string;
  search?: string;
  country_code?: string;
  job_title_id?: number;
  sort_by?: "full_name" | "salary" | "hired_at" | "updated_at" | "employee_code";
  sort_dir?: "asc" | "desc";
};
