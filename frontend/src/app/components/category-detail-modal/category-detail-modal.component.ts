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
  @Output() close = new EventEmitter<void>();

  activeTab = signal<TabType>('resumen');
  showAddExpenseForm = signal(false);
  showAddAporteForm = signal(false);

  // Tipo de gasto a agregar
  expenseType = signal<'fijo' | 'variable'>('fijo');

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
      e.categoria_id === this.category._id && e.tipo === TipoGasto.FIJO
    )
  );

  gastosVariables = computed(() =>
    this.expenseService.expenses().filter(e =>
      e.categoria_id === this.category._id && e.tipo === TipoGasto.VARIABLE
    )
  );

  aportes = computed(() =>
    this.aporteService.aportes().filter(a =>
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

  totalReal = computed(() =>
    this.totalGastosFijos() + this.totalGastosVariables() - this.totalAportes()
  );

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
    // Cargar gastos y aportes de esta categoría
    this.loadCategoryData();
  }

  loadCategoryData() {
    this.expenseService.getExpenses(this.periodoId, undefined, this.category._id).subscribe();
    this.aporteService.getAportes(this.periodoId, undefined, this.category._id).subscribe();
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
    this.expenseForm = {
      nombre: '',
      monto: 0,
      tipo: this.expenseType() === 'fijo' ? TipoGasto.FIJO : TipoGasto.VARIABLE,
      es_permanente: true,
      periodos_restantes: 0,
      descripcion: ''
    };
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
    this.aporteForm = {
      nombre: '',
      monto: 0,
      es_fijo: true,
      descripcion: ''
    };
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
}
