from django.apps import AppConfig
import os


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = "Auditoria"

    def ready(self):
        # Só roda no processo principal do runserver (evita 2x)
        if os.environ.get("RUN_MAIN") != "true":
            return
        try:
            from .services import auditar_sistema
            r = auditar_sistema()
            total = (
                len(r["produtos_sem_100"])
                + len(r["insumos_sem_densidade"])
                + len(r["receitas_com_balanco_ruim"])
            )
            if total == 0:
                print("\n✅ Auditoria: tudo OK.\n")
                return
            print("\n" + "=" * 60)
            print("⚠️  AUDITORIA — TAREFAS PENDENTES")
            print("=" * 60)
            if r["produtos_sem_100"]:
                print("\n🔴 Produtos com soma de % ≠ 100:")
                for p in r["produtos_sem_100"]:
                    print(f"   - {p['product']}: soma = {p['soma']}% "
                          f"(faltam {p['faltam']}%)")
            if r["insumos_sem_densidade"]:
                print("\n🟡 Insumos de volume sem densidade:")
                for i in r["insumos_sem_densidade"]:
                    print(f"   - {i['food_ingredient']} ({i['unit']})")
            if r["receitas_com_balanco_ruim"]:
                print("\n🟠 Receitas com balanço de massa ruim:")
                for rec in r["receitas_com_balanco_ruim"]:
                    print(f"   - {rec['receita']}: "
                          f"input={rec['peso_input_g']}g, "
                          f"output={rec['size']}g, "
                          f"diferença={rec['diferenca_pct']}% "
                          f"({rec['classificacao']})")
            print("\n" + "=" * 60 + "\n")
        except Exception as e:
            print(f"\n⚠️  Auditoria falhou: {e}\n")
