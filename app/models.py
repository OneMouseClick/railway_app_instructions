"""
Нормализованная (не привязанная к формату файла) модель данных
техпаспорта. Это промежуточный слой между сырым документом
(RawDocument из parsers/base.py) и итоговым JSON, повторяющим
структуру инструкции.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PathBoundary:
    path_number: Optional[str] = None
    from_label: Optional[str] = None      # напр. 'ПС СП561 Знак ГПНП ООО «МеталлСнаб» ПК0+43,56'
    to_label: Optional[str] = None        # напр. 'Упор ПК2+12,56'
    specialization: Optional[str] = None  # 'Погрузочно-выгрузочный'
    length_full_m: Optional[float] = None
    length_useful_m: Optional[float] = None


@dataclass
class TrackSuperstructure:
    """Данные раздела 3 «Верхнее строение пути» — по путям предприятия."""
    path_number: Optional[str] = None
    ballast_type: Optional[str] = None          # Табл. 3.1
    ballast_thickness: Optional[str] = None      # Табл. 3.2
    ballast_pollution: Optional[str] = None       # Табл. 3.3
    ballast_pollutability: Optional[str] = None   # Табл. 3.4
    sleepers_summary: Optional[str] = None        # Табл. 3.5 (эпюра/материал/кол-во)
    rails_summary: Optional[str] = None           # Табл. 3.6/3.9 (тип, длина)
    welded_joints: Optional[str] = None           # Табл. 3.7
    joint_fasteners: Optional[str] = None         # Табл. 3.10
    intermediate_fasteners: Optional[str] = None  # Табл. 3.11
    anti_creepers: Optional[str] = None           # Табл. 3.12


@dataclass
class CargoFront:
    id: Optional[str] = None                # 'ГФ1'
    name: Optional[str] = None              # 'Рампа (справа)'
    path_number: Optional[str] = None
    from_picket: Optional[str] = None
    to_picket: Optional[str] = None
    length_m: Optional[float] = None
    capacity: Optional[str] = None          # '3 кр.' / '32 пв. 30пл.'
    daily_turnover: Optional[str] = None    # из описательного текста
    cargo_list: Optional[str] = None        # перечень перерабатываемых грузов
    dangerous_cargo: Optional[str] = None
    mechanization: Optional[str] = None     # средства механизации


@dataclass
class SafetyDevice:
    """Раздел «Наличие предохранительных устройств»."""
    device_type: Optional[str] = None       # 'Ручной сбрасывающий башмак'
    device_id: Optional[str] = None         # 'СБР№583а' / 'СБ02'
    picket: Optional[str] = None            # 'ПК1+04,86'
    throw_direction: Optional[str] = None   # 'вправо'


@dataclass
class GeneralInfo:
    company_name: Optional[str] = None
    station_name: Optional[str] = None
    path_numbers: list[str] = field(default_factory=list)
    junction_text: Optional[str] = None         # «Место примыкания...» сырой текст
    boundary_text: Optional[str] = None         # «Границы...» сырой текст
    safety_devices: list[SafetyDevice] = field(default_factory=list)
    contract_text: Optional[str] = None
    service_order_text: Optional[str] = None    # «Порядок подачи и уборки вагонов...»
    locomotive_series: list[str] = field(default_factory=list)  # ['ТЭМ2', 'ТЭМ18']


@dataclass
class TechPassportData:
    source_file: Optional[str] = None
    source_format: Optional[str] = None   # 'doc' | 'docx' | 'pdf'

    general: GeneralInfo = field(default_factory=GeneralInfo)
    path_boundaries: list[PathBoundary] = field(default_factory=list)  # Табл. 1.2/1.3
    total_length_full_m: Optional[float] = None
    total_length_useful_m: Optional[float] = None

    embankments_present: Optional[bool] = None     # Табл. 2.1
    drainage_present: Optional[bool] = None        # Табл. 2.2
    deformation_present: Optional[bool] = None     # Табл. 2.3
    structures_present: Optional[bool] = None      # Табл. 2.4
    road_crossings_present: Optional[bool] = None  # Табл. 2.5

    track_superstructure: list[TrackSuperstructure] = field(default_factory=list)
    switches_summary: Optional[str] = None   # Табл. 3.8 (ведомость стрелочных переводов)

    cargo_fronts: list[CargoFront] = field(default_factory=list)

    # "сырые" таблицы по номеру — для полей, для которых пока нет
    # специализированного экстрактора, но данные уже лежат наготове
    # и не потеряны
    raw_tables_by_number: dict[str, str] = field(default_factory=dict)
