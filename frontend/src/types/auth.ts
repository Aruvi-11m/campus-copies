export interface Admin {
  id: string;
  username: string;
  full_name: string;
}

export interface AuthResponse {
  token: string;
  admin: Admin;
}

export interface Student {
  id: string;
  mobile_number: string;
  name?: string;
  email?: string;
  college_name?: string;
  degree?: string;
  semester?: number;
}
