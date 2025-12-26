import { Component, Input, Output, EventEmitter, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Category, Expense, Aporte, TipoGasto } from '../../models';
import { ExpenseService } from '../../services/expense.service';
import { AporteService } from '../../services/aporte.service';

type TabType = 'resumen' | 'fijos' | 'variables' | 'aportes';

@Component({
  selector: 'app-category-detail-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './category-detail-modal.component.html',
  styleUrl: './category-detail-modal.component.css'
})
export class CategoryDetailModalComponent implements OnInit {
  @Input() category!: Category;
  @Input() periodoId!: string;
  @Input() meta?: number;
  @Input() periodoFechaInicio?: Date;
  @Input() periodoFechaFin?: Date;
  @Output() close = new EventEmitter<void>();
  @Output() metaChanged = new EventEmitter<number>();

  activeTab = signal<TabType>('resumen');
  showAddExpenseForm = signal(false);
  showAddAporteForm = signal(false);
  editingMeta = signal(false);
  metaEditValue = signal(0);

  // Tipo de gasto a agregar
  expenseType = signal<'fijo' | 'variable'>('fijo');

  // Computed: Es categoría de crédito?
  isCredito = computed(() => this.category.slug === 'credito');

  // Formulario de gasto fijo
  expenseForm = {
    nombre: '',
    monto: 0,
    tipo: TipoGasto.FIJO,
    es_permanente: true,
    periodos_restantes: 0,
    descripcion: ''
  };

  // Formulario de aporte
  aporteForm = {
    nombre: '',
    monto: 0,
    es_fijo: true,
    descripcion: ''
  };

  // Datos computados
  gastosFijos = computed(() =>
    this.expenseService.expenses().filter(e =>
      e.periodo_id === this.periodoId &&
      e.categoria_id === this.category._id &&
      e.tipo === TipoGasto.FIJO
    )
  );

  gastosVariables = computed(() =>
    this.expenseService.expenses().filter(e =>
      e.periodo_id === this.periodoId &&
      e.categoria_id === this.category._id &&
      e.tipo === TipoGasto.VARIABLE
    )
  );

  aportes = computed(() =>
    this.aporteService.aportes().filter(a =>
      a.periodo_id === this.periodoId &&
      a.categoria_id === this.category._id
    )
  );

  totalGastosFijos = computed(() =>
    this.gastosFijos().reduce((sum, e) => sum + e.monto, 0)
  );

  totalGastosVariables = computed(() =>
    this.gastosVariables().reduce((sum, e) => sum + e.monto, 0)
  );

  totalAportes = computed(() =>
    this.aportes().reduce((sum, a) => sum + a.monto, 0)
  );

  // Para crédito: Total Gastado (sin restar aportes, porque no existen en crédito)
  totalGastado = computed(() =>
    this.totalGastosFijos() + this.totalGastosVariables()
  );

  // Para otras categorías: Total Real (gastos - aportes)
  totalReal = computed(() => {
    if (this.isCredito()) {
      return this.totalGastado();
    }
    return this.totalGastosFijos() + this.totalGastosVariables() - this.totalAportes();
  });

  // Crédito Disponible (para crédito) o Disponible (para otras categorías)
  disponible = computed(() => {
    if (this.meta) {
      return this.meta - this.totalReal();
    }
    return 0;
  });

  constructor(
    public expenseService: ExpenseService,
    public aporteService: AporteService
  ) {}

  ngOnInit() {
    // Inicializar valor de meta para edición
    this.metaEditValue.set(this.meta || 0);

    // Cargar gastos y aportes de esta categoría
    console.log('DEBUG MODAL: ngOnInit', {
      categoria: this.category.nombre,
      periodoId: this.periodoId,
      categoriaId: this.category._id,
      isCredito: this.isCredito(),
      meta: this.meta,
      periodoFechaInicio: this.periodoFechaInicio,
      periodoFechaFin: this.periodoFechaFin
    });
    this.loadCategoryData();
  }

  loadCategoryData() {
    console.log('DEBUG MODAL: loadCategoryData', {
      periodoId: this.periodoId,
      categoriaId: this.category._id
    });

    // Cargar gastos (todos tienen gastos)
    this.expenseService.getExpenses(this.periodoId, undefined, this.category._id).subscribe(expenses => {
      console.log('DEBUG MODAL: Expenses cargados:', expenses);
      console.log('DEBUG MODAL: Total expenses en servicio:', this.expenseService.expenses());
      console.log('DEBUG MODAL: Gastos fijos filtrados:', this.gastosFijos());
      console.log('DEBUG MODAL: Gastos variables filtrados:', this.gastosVariables());
    });

    // Solo cargar aportes si NO es crédito
    if (!this.isCredito()) {
      this.aporteService.getAportes(this.periodoId, undefined, this.category._id).subscribe(aportes => {
        console.log('DEBUG MODAL: Aportes cargados:', aportes);
        console.log('DEBUG MODAL: Total aportes en servicio:', this.aporteService.aportes());
        console.log('DEBUG MODAL: Aportes filtrados:', this.aportes());
      });
    }
  }

  setActiveTab(tab: TabType) {
    this.activeTab.set(tab);
  }

  onClose() {
    this.close.emit();
  }

  // ==================
  // GASTOS FIJOS
  // ==================

  openAddExpenseForm(tipo: 'fijo' | 'variable') {
    this.expenseType.set(tipo);
    this.resetExpenseForm();
    this.showAddExpenseForm.set(true);
  }

  resetExpenseForm() {
    this.expenseForm.nombre = '';
    this.expenseForm.monto = 0;
    this.expenseForm.tipo = this.expenseType() === 'fijo' ? TipoGasto.FIJO : TipoGasto.VARIABLE;
    this.expenseForm.es_permanente = true;
    this.expenseForm.periodos_restantes = 0;
    this.expenseForm.descripcion = '';
  }

  cancelExpenseForm() {
    this.showAddExpenseForm.set(false);
    this.resetExpenseForm();
  }

  async saveExpense() {
    if (!this.expenseForm.nombre || this.expenseForm.monto <= 0) {
      alert('Por favor completa todos los campos requeridos');
      return;
    }

    try {
      const expenseCreate: any = {
        nombre: this.expenseForm.nombre,
        monto: this.expenseForm.monto,
        categoria_id: this.category._id,
        tipo: this.expenseForm.tipo,
        descripcion: this.expenseForm.descripcion || undefined
      };

      // Solo agregar campos de gasto fijo si corresponde
      if (this.expenseType() === 'fijo') {
        expenseCreate.es_permanente = this.expenseForm.es_permanente;

        if (!this.expenseForm.es_permanente) {
          expenseCreate.periodos_restantes = this.expenseForm.periodos_restantes;
        }
      }

      await this.expenseService.createExpense(this.periodoId, expenseCreate).toPromise();

      this.showAddExpenseForm.set(false);
      this.resetExpenseForm();
      this.loadCategoryData();
    } catch (error) {
      console.error('Error al crear gasto:', error);
      alert('Error al crear el gasto');
    }
  }

  async deleteExpense(expenseId: string) {
    if (!confirm('¿Estás seguro de eliminar este gasto?')) return;

    try {
      await this.expenseService.deleteExpense(expenseId).toPromise();
      this.loadCategoryData();
    } catch (error) {
      console.error('Error al eliminar gasto:', error);
      alert('Error al eliminar el gasto');
    }
  }

  // ==================
  // APORTES
  // ==================

  openAddAporteForm() {
    this.resetAporteForm();
    this.showAddAporteForm.set(true);
  }

  resetAporteForm() {
    this.aporteForm.nombre = '';
    this.aporteForm.monto = 0;
    this.aporteForm.es_fijo = true;
    this.aporteForm.descripcion = '';
  }

  cancelAporteForm() {
    this.showAddAporteForm.set(false);
    this.resetAporteForm();
  }

  async saveAporte() {
    if (!this.aporteForm.nombre || this.aporteForm.monto <= 0) {
      alert('Por favor completa todos los campos requeridos');
      return;
    }

    try {
      const aporteCreate = {
        nombre: this.aporteForm.nombre,
        monto: this.aporteForm.monto,
        categoria_id: this.category._id,
        es_fijo: this.aporteForm.es_fijo,
        descripcion: this.aporteForm.descripcion || undefined
      };

      await this.aporteService.createAporte(this.periodoId, aporteCreate).toPromise();

      this.showAddAporteForm.set(false);
      this.resetAporteForm();
      this.loadCategoryData();
    } catch (error) {
      console.error('Error al crear aporte:', error);
      alert('Error al crear el aporte');
    }
  }

  async deleteAporte(aporteId: string) {
    if (!confirm('¿Estás seguro de eliminar este aporte?')) return;

    try {
      await this.aporteService.deleteAporte(aporteId).toPromise();
      this.loadCategoryData();
    } catch (error) {
      console.error('Error al eliminar aporte:', error);
      alert('Error al eliminar el aporte');
    }
  }

  // Helpers
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(value);
  }

  getExpenseLabel(expense: Expense): string {
    if (expense.tipo === TipoGasto.VARIABLE) return expense.nombre;

    if (expense.es_permanente) {
      return `${expense.nombre} (Permanente)`;
    } else {
      return `${expense.nombre} (${expense.periodos_restantes} cuotas restantes)`;
    }
  }

  getAporteLabel(aporte: Aporte): string {
    return aporte.es_fijo ? `${aporte.nombre} (Fijo)` : aporte.nombre;
  }

  // ==================
  // EDITAR META
  // ==================

  startEditingMeta() {
    this.metaEditValue.set(this.meta || 0);
    this.editingMeta.set(true);
  }

  cancelEditingMeta() {
    this.editingMeta.set(false);
    this.metaEditValue.set(this.meta || 0);
  }

  saveMeta() {
    if (this.metaEditValue() <= 0) {
      alert('La meta debe ser mayor a 0');
      return;
    }

    this.metaChanged.emit(this.metaEditValue());
    this.editingMeta.set(false);
  }

  // ==================
  // HELPERS
  // ==================

  formatDate(date?: Date): string {
    if (!date) return '';
    return new Date(date).toLocaleDateString('es-CL', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  }

  getPorcentajeUsado(): number {
    if (!this.meta || this.meta === 0) return 0;
    return Math.round((this.totalReal() / this.meta) * 100);
  }
}
