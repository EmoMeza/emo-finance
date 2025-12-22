/**
 * Modelos de Aporte según LOGICA_SISTEMA.md
 */

export interface Aporte {
  _id: string;
  user_id: string;
  periodo_id: string;
  categoria_id: string;
  nombre: string;
  monto: number;
  es_fijo: boolean;
  descripcion?: string;
  fecha_registro: string;
  created_at: string;
  updated_at: string;
}

export interface AporteCreate {
  nombre: string;
  monto: number;
  categoria_id: string;
  es_fijo: boolean;
  descripcion?: string;
}

export interface AporteUpdate {
  nombre?: string;
  monto?: number;
  descripcion?: string;
}
