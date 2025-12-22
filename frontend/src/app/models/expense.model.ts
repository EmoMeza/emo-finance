/**
 * Modelos de Gasto según LOGICA_SISTEMA.md
 */

export enum TipoGasto {
  FIJO = 'fijo',
  VARIABLE = 'variable'
}

export interface Expense {
  _id: string;
  user_id: string;
  periodo_id: string;
  categoria_id: string;
  nombre: string;
  monto: number;
  tipo: TipoGasto;
  es_permanente?: boolean;
  periodos_restantes?: number;
  descripcion?: string;
  fecha_registro: string;
  created_at: string;
  updated_at: string;
}

export interface ExpenseCreate {
  nombre: string;
  monto: number;
  categoria_id: string;
  tipo: TipoGasto;
  es_permanente?: boolean;
  periodos_restantes?: number;
  descripcion?: string;
}

export interface ExpenseUpdate {
  nombre?: string;
  monto?: number;
  descripcion?: string;
}
