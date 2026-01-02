import { Component, Input, Output, EventEmitter, signal, computed, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Category, Expense, Aporte, TipoGasto } from '../../models';
import { ExpenseService } from '../../services/expense.service';
import { AporteService } from '../../services/aporte.service';
import { PeriodService } from '../../services/period.service';

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
  @Output() periodChanged = new EventEmitter<void>();

  activeTab = signal<TabType>('resumen');
  showAddExpenseForm = signal(false);
  showAddAporteForm = signal(false);
  editingMeta = signal(false);
  metaEditValue = signal(0);
  editingFechaFin = signal(false);
  fechaFinEditValue = '';

  // Control de edición
  editingExpenseId = signal<string | null>(null);
  editingAporteId = signal<string | null>(null);

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
    public aporteService: AporteService,
    private periodService: PeriodService
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
    this.editingExpenseId.set(null);
    this.resetExpenseForm();
    this.showAddExpenseForm.set(true);
  }

  editExpense(expense: Expense) {
    this.editingExpenseId.set(expense._id);
    this.expenseType.set(expense.tipo === TipoGasto.FIJO ? 'fijo' : 'variable');
    this.expenseForm.nombre = expense.nombre;
    this.expenseForm.monto = expense.monto;
    this.expenseForm.tipo = expense.tipo;
    this.expenseForm.es_permanente = expense.es_permanente ?? true;
    this.expenseForm.periodos_restantes = expense.periodos_restantes ?? 0;
    this.expenseForm.descripcion = expense.descripcion ?? '';
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
    this.editingExpenseId.set(null);
    this.resetExpenseForm();
  }

  async saveExpense() {
    if (!this.expenseForm.nombre || this.expenseForm.monto <= 0) {
      alert('Por favor completa todos los campos requeridos');
      return;
    }

    try {
      const expenseData: any = {
        nombre: this.expenseForm.nombre,
        monto: this.expenseForm.monto,
        descripcion: this.expenseForm.descripcion || undefined
      };

      // Solo agregar campos de gasto fijo si corresponde
      if (this.expenseType() === 'fijo') {
        expenseData.es_permanente = this.expenseForm.es_permanente;

        if (!this.expenseForm.es_permanente) {
          expenseData.periodos_restantes = this.expenseForm.periodos_restantes;
        }
      }

      const editingId = this.editingExpenseId();
      if (editingId) {
        // Actualizar gasto existente
        await this.expenseService.updateExpense(editingId, expenseData).toPromise();
      } else {
        // Crear nuevo gasto
        expenseData.categoria_id = this.category._id;
        expenseData.tipo = this.expenseForm.tipo;
        await this.expenseService.createExpense(this.periodoId, expenseData).toPromise();
      }

      this.showAddExpenseForm.set(false);
      this.editingExpenseId.set(null);
      this.resetExpenseForm();
      this.loadCategoryData();
    } catch (error) {
      console.error('Error al guardar gasto:', error);
      alert('Error al guardar el gasto');
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
    this.editingAporteId.set(null);
    this.resetAporteForm();
    this.showAddAporteForm.set(true);
  }

  editAporte(aporte: Aporte) {
    this.editingAporteId.set(aporte._id);
    this.aporteForm.nombre = aporte.nombre;
    this.aporteForm.monto = aporte.monto;
    this.aporteForm.es_fijo = aporte.es_fijo ?? true;
    this.aporteForm.descripcion = aporte.descripcion ?? '';
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
    this.editingAporteId.set(null);
    this.resetAporteForm();
  }

  async saveAporte() {
    if (!this.aporteForm.nombre || this.aporteForm.monto <= 0) {
      alert('Por favor completa todos los campos requeridos');
      return;
    }

    try {
      const aporteData = {
        nombre: this.aporteForm.nombre,
        monto: this.aporteForm.monto,
        es_fijo: this.aporteForm.es_fijo,
        descripcion: this.aporteForm.descripcion || undefined
      };

      const editingId = this.editingAporteId();
      if (editingId) {
        // Actualizar aporte existente
        await this.aporteService.updateAporte(editingId, aporteData).toPromise();
      } else {
        // Crear nuevo aporte
        const aporteCreate = {
          ...aporteData,
          categoria_id: this.category._id
        };
        await this.aporteService.createAporte(this.periodoId, aporteCreate).toPromise();
      }

      this.showAddAporteForm.set(false);
      this.editingAporteId.set(null);
      this.resetAporteForm();
      this.loadCategoryData();
    } catch (error) {
      console.error('Error al guardar aporte:', error);
      alert('Error al guardar el aporte');
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
  // EDITAR FECHA FIN
  // ==================

  startEditingFechaFin() {
    // Convertir fecha actual a formato YYYY-MM-DD para el input type="date"
    if (this.periodoFechaFin) {
      const date = new Date(this.periodoFechaFin);
      this.fechaFinEditValue = date.toISOString().split('T')[0];
    }
    this.editingFechaFin.set(true);
  }

  cancelEditingFechaFin() {
    this.editingFechaFin.set(false);
    this.fechaFinEditValue = '';
  }

  async saveFechaFin() {
    if (!this.fechaFinEditValue) {
      alert('Por favor selecciona una fecha válida');
      return;
    }

    // Validar que la nueva fecha sea posterior a fecha_inicio
    const nuevaFechaFin = new Date(this.fechaFinEditValue);
    if (this.periodoFechaInicio && nuevaFechaFin <= new Date(this.periodoFechaInicio)) {
      alert('La fecha de fin debe ser posterior a la fecha de inicio');
      return;
    }

    try {
      // Actualizar la fecha_fin del período
      await this.periodService.updatePeriod(this.periodoId, {
        fecha_fin: nuevaFechaFin
      }).toPromise();

      // Notificar al componente padre para que recargue los datos
      this.periodChanged.emit();
      this.editingFechaFin.set(false);
      alert('Fecha de cierre actualizada correctamente');
    } catch (error) {
      console.error('Error al actualizar fecha de cierre:', error);
      alert('Error al actualizar la fecha de cierre');
    }
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
