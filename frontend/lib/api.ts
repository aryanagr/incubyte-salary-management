import type { CountryInsight, Employee, EmployeeInput, EmployeeList, ReferenceData } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as {
        detail?: string | { message?: string } | Array<{ msg?: string; loc?: Array<string | number> }>;
      };
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) {
        const first = body.detail[0];
        if (first?.msg) message = first.msg;
      } else if (body.detail?.message) message = body.detail.message;
    } catch {
      // Preserve stable generic error if body is not JSON.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function getReferenceData() {
  return request<ReferenceData>("/api/v1/reference-data");
}

export function getEmployees(params: Record<string, string | number | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  return request<EmployeeList>(`/api/v1/employees?${search.toString()}`);
}

export function createEmployee(input: EmployeeInput) {
  return request<Employee>("/api/v1/employees", { method: "POST", body: JSON.stringify(input) });
}

export function updateEmployee(id: number, input: Partial<EmployeeInput>) {
  return request<Employee>(`/api/v1/employees/${id}`, { method: "PATCH", body: JSON.stringify(input) });
}

export function deleteEmployee(id: number) {
  return request<void>(`/api/v1/employees/${id}`, { method: "DELETE" });
}

export function getCountryInsight(countryCode: string) {
  return request<CountryInsight>(`/api/v1/insights/countries/${countryCode}`);
}
