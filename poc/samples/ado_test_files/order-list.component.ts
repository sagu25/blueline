import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { OrderService } from '../services/order.service';

interface Order {
  id: number;
  reference: string;
  status: string;
  totalAmount: number;
  createdDate: string;
}

@Component({
  selector: 'app-order-list',
  templateUrl: './order-list.component.html',
  styleUrls: ['./order-list.component.scss']
  // minor: missing changeDetection: ChangeDetectionStrategy.OnPush
})
export class OrderListComponent implements OnInit, OnDestroy {

  orders: Order[] = [];
  isLoading = false;
  errorMessage = '';

  // Used for subscription cleanup — good pattern
  private destroy$ = new Subject<void>();

  // minor: pageSize is a magic number — could be a named constant
  pageSize = 20;
  currentPage = 1;

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.orderService.getOrders(this.currentPage, this.pageSize)
      .pipe(takeUntil(this.destroy$))   // correctly unsubscribed
      .subscribe({
        next: (orders: Order[]) => {
          this.orders = orders;
          this.isLoading = false;
        },
        error: (err: Error) => {
          // minor: exposes err.message directly to UI — should use a generic user-facing message
          this.errorMessage = err.message;
          this.isLoading = false;
        }
      });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadOrders();
  }

  // minor: filter logic in component — should be in service or pipe
  getActiveOrders(): Order[] {
    return this.orders.filter(o => o.status === 'Active' || o.status === 'Pending');
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
