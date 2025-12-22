/**
 * Modelos de Categoría según LOGICA_SISTEMA.md
 */

export enum TipoCategoria {
  AHORRO = 'ahorro',
  ARRIENDO = 'arriendo',
  CREDITO = 'credito',
  LIQUIDEZ = 'liquidez'
}

export interface Category {
  _id: string;
  user_id: string;
  nombre: string;
  slug: TipoCategoria;
  icono: string;
  color: string;
  tiene_meta: boolean;
  descripcion?: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  nombre: string;
  slug: TipoCategoria;
  icono: string;
  color: string;
  tiene_meta: boolean;
  descripcion?: string;
}

export interface CategoryUpdate {
  nombre?: string;
  icono?: string;
  color?: string;
  descripcion?: string;
}
