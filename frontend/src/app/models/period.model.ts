/**
 * Modelos de Período según LOGICA_SISTEMA.md
 */

export enum TipoPeriodo {
  MENSUAL_ESTANDAR = 'mensual_estandar',
  CICLO_CREDITO = 'ciclo_credito'
}

export enum EstadoPeriodo {
  ACTIVO = 'activo',
  CERRADO = 'cerrado',
  PROYECTADO = 'proyectado'
}

export interface MetasCategorias {
  credito_usable: number;
  // NOTA: Ahorro y Arriendo NO tienen meta, se calculan como suma de gastos - aportes
}

export interface Period {
  _id: string;
  user_id: string;
  tipo_periodo: TipoPeriodo;
  fecha_inicio: string;
  fecha_fin: string;
  sueldo: number;
  metas_categorias: MetasCategorias;
  estado: EstadoPeriodo;
  categorias: string[]; // IDs de las 4 categorías del período
  total_gastado: number;
  created_at: string;
  updated_at: string;
}

export interface PeriodCreate {
  tipo_periodo: TipoPeriodo;
  fecha_inicio: string;
  fecha_fin: string;
  sueldo?: number;
  metas_categorias?: MetasCategorias;
  estado?: EstadoPeriodo;
  total_gastado?: number;
}

export interface PeriodUpdate {
  sueldo?: number;
  metas_categorias?: MetasCategorias;
  estado?: EstadoPeriodo;
  total_gastado?: number;
}

export interface CategorySummary {
  categoria_id: string;
  categoria_slug: string;
  categoria_nombre: string;
  total_gastos: number;
  total_aportes: number;
  total_real: number;
  meta?: number;
}

export interface PeriodSummary {
  period: Period;
  categories_summary: CategorySummary[];
  liquidez_calculada: number;
}
