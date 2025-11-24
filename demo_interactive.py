from vos.core.vm import VM, PAGE_SIZE

print("=== DEMO INTERACTIVA ===\n")

vm = VM()

print("1. Escribiendo valor 42 en dirección 100:")
vm.write_byte(100, 42)

print("\n2. Leyendo de dirección 100:")
value = vm.read_byte(100)
print(f"   Valor leído: {value}")

print("\n3. Estadísticas del simulador:")
stats = vm.get_stats()
for key, val in stats.items():
    print(f"   - {key}: {val}")

print("\n✅ Demo completada!")