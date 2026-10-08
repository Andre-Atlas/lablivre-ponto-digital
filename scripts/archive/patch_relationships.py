with open("backend/app/adapters/persistence/orm_models.py", "r") as f:
    content = f.read()

# Fix relationships in User model
content = content.replace(
    'devices: Mapped[List["Device"]] = relationship(back_populates="user")',
    'devices: Mapped[List["Device"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)'
)
content = content.replace(
    'checkins: Mapped[List["Checkin"]] = relationship(back_populates="user")',
    'checkins: Mapped[List["Checkin"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)'
)

# Fix relationships in Device model
content = content.replace(
    'checkins: Mapped[List["Checkin"]] = relationship(back_populates="device")',
    'checkins: Mapped[List["Checkin"]] = relationship(back_populates="device", cascade="all, delete-orphan", passive_deletes=True)'
)

# Fix relationships in Checkin model
content = content.replace(
    'duplicatas: Mapped[List["CheckinDuplicata"]] = relationship(back_populates="checkin_original")',
    'duplicatas: Mapped[List["CheckinDuplicata"]] = relationship(back_populates="checkin_original", cascade="all, delete-orphan", passive_deletes=True)'
)

with open("backend/app/adapters/persistence/orm_models.py", "w") as f:
    f.write(content)
