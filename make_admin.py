
"""
Uso:
    python make_admin.py <supabase_user_id>

Ejemplo:
    python make_admin.py "550e8400-e29b-41d4-a716-446655440000"
"""

import sys
import os
from pathlib import Path


project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
env_file = project_root / ".env"
if not env_file.exists():
    print("❌ Error: No se encontró el archivo .env")
    print("   Crea un archivo .env con las variables de configuración")
    sys.exit(1)

try:
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal, engine
    from app.api.models.user import UserProfile, Role
    from app.api.repositories.user_repository import UserRepository
    from app.api.repositories.role_repository import RoleRepository
    from app.config import settings
    import uuid
except Exception as e:
    print(f"❌ Error al importar módulos: {e}")
    print("\nPosibles causas:")
    print("1. Archivo .env mal formateado")
    print("2. DATABASE_URL vacía o incorrecta")
    print("3. Variables de entorno faltantes")
    print("\nRevisa tu archivo .env y asegúrate de que tenga:")
    print("DATABASE_URL=postgresql://usuario:password@host:puerto/database")
    print("SUPABASE_PROJECT_ID=tu_project_id")
    print("SUPABASE_ANON_KEY=tu_anon_key")
    sys.exit(1)


def create_admin_role_if_not_exists(db: Session) -> Role:

    role_repo = RoleRepository(db)
    
    admin_role = role_repo.get_by_name("admin")
    if admin_role:
        print(f"✅ El rol 'admin' ya existe con ID: {admin_role.id}")
        return admin_role
    
    print("📝 Creando rol de administrador...")
    admin_role_data = {
        "name": "admin",
        "description": "Administrator. Full access to all system features.",
        "permissions": ["admin.*"]
    }
    
    admin_role = role_repo.create(admin_role_data)
    print(f"✅ Rol 'admin' creado con ID: {admin_role.id}")
    return admin_role


def create_user_profile_if_not_exists(db: Session, supabase_user_id: str, admin_role: Role) -> UserProfile:

    user_repo = UserRepository(db)
    
    user_profile = user_repo.get_by_supabase_id(supabase_user_id)
    if user_profile:
        print(f"✅ El usuario ya tiene perfil con ID: {user_profile.id}")
        return user_profile
    
    print("👤 Creando perfil de usuario...")
    
    full_name = "Administrator"  
    try:
        from app.core.security import supabase
        user_response = supabase.auth.admin.get_user_by_id(supabase_user_id)
        if user_response.user:
            # Intentar obtener el nombre de user_metadata
            user_metadata = user_response.user.user_metadata or {}
            full_name = (
                user_metadata.get("full_name") or 
                user_metadata.get("name") or 
                user_response.user.email or 
                "Administrator"
            )
            print(f"📝 Nombre obtenido de Supabase: {full_name}")
    except Exception as e:
        print(f"⚠️ No se pudo obtener info de Supabase: {e}")
        print("📝 Usando nombre por defecto: Administrator")
    
    user_data = {
        "supabase_user_id": supabase_user_id,
        "full_name": full_name,
        "role_id": admin_role.id,
        "user_metadata": {"created_by_script": True, "made_admin_at": datetime.utcnow().isoformat()}
    }
    
    user_profile = user_repo.create(user_data)
    print(f"✅ Perfil de usuario creado con ID: {user_profile.id}")
    return user_profile


def assign_admin_role(supabase_user_id: str) -> bool:
    
    try:
        uuid.UUID(supabase_user_id)
    except ValueError:
        print(f"❌ Error: '{supabase_user_id}' no es un UUID válido")
        return False
    
    print(f"🔧 Procesando usuario: {supabase_user_id}")
    
    db = SessionLocal()
    try:
        admin_role = create_admin_role_if_not_exists(db)
        user_repo = UserRepository(db)
        user_profile = user_repo.get_by_supabase_id(supabase_user_id)
        
        if not user_profile:
            user_profile = create_user_profile_if_not_exists(db, supabase_user_id, admin_role)
        else:
            print(f"👤 Usuario encontrado: {user_profile.full_name or 'Sin nombre'}")
            
            if user_profile.role_id == admin_role.id:
                print("✅ El usuario ya tiene permisos de administrador")
                return True
            
            print("🔄 Asignando rol de administrador...")
            updated_user = user_repo.update_user_role(user_profile.id, admin_role.id)
            
            if updated_user:
                print("✅ Rol de administrador asignado exitosamente")
                print(f"📝 Manteniendo nombre existente: {user_profile.full_name or 'Sin nombre'}")
            else:
                print("❌ Error al asignar el rol de administrador")
                return False
        
        final_user = user_repo.get_with_role(user_profile.id)
        if final_user and final_user.role and final_user.role.name == "admin":
            print(f"✅ Verificación exitosa: {final_user.full_name or 'Usuario'} ahora es administrador")
            print(f"   - Permisos: {final_user.role.permissions}")
            return True
        else:
            print("❌ Error: No se pudo verificar la asignación del rol")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el proceso: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    if len(sys.argv) != 2:
        print("❌ Uso incorrecto")
        print("   Uso: python make_admin.py <supabase_user_id>")
        print("   Ejemplo: python make_admin.py '550e8400-e29b-41d4-a716-446655440000'")
        sys.exit(1)
    
    supabase_user_id = sys.argv[1].strip()
    
    print("="*60)
    print(f"🚀 {settings.PROJECT_NAME} - Script de Asignación de Admin")
    print("="*60)
    print(f"📋 Supabase User ID: {supabase_user_id}")
    print(f"🌍 Entorno: {settings.ENVIRONMENT}")
    print("-"*60)
    
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a la base de datos exitosa")
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        sys.exit(1)
    
    success = assign_admin_role(supabase_user_id)
    
    print("-"*60)
    if success:
        print("🎉 ¡Proceso completado exitosamente!")
        print("   El usuario ahora tiene permisos de administrador.")
    else:
        print("💥 Proceso fallido. Revisa los errores anteriores.")
        sys.exit(1)
    
    print("="*60)


if __name__ == "__main__":
    main()